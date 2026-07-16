# Messaging Service

Target: 200M messages/day (2314 msg/s avg, 7k peak)

## Data Models

- `conversations`: id, user1_id, user2_id (sorted unique), created_at, last_message_at, last_message_text
- `messages`: id, conversation_id, sender_id, content, media_asset_id, message_type (text,image,video,system), is_read, read_at, created_at, reply_to_message_id, is_deleted

Partitioning plan:
- Conversation table small (maybe 25M conversations if 50% of users match 1). Fits single Postgres.
- Message table massive: 200M/day = 73B/year. Must partition by RANGE created_at monthly + maybe hash conversation_id % 16.

## Write Flow

1. `POST /conversations/{id}/messages`
   - Auth + check access (user in conversation)
   - Rate limit Redis INCR per minute (60 msg/min per user)
   - Validation: content or media required
   - Insert message row
   - Update conversation last_message_at, last_message_text in same TX plus update match last_message_at for sorting matches feed
   - Publish event `MESSAGE_SENT`
   - WebSocket broadcast: schedule async task `manager.broadcast_to_conversation`

2. WS broadcast:
   - `ConnectionManager` holds dict user_id -> [WebSocket]
   - `send_personal_message` iterates sockets, tries send, removes dead.
   - Also publishes to Redis channel `ws:user:{id}` for horizontal scaling. Other nodes subscribe via background task (not implemented in MVP but designed).

3. Offline handling:
   - Unread count via query count is_read=False.
   - Push notification fallback when recipient not in active_connections (check via redis online set). Would call FCM.

## Read Flow

- `GET /conversations`: list conversations sorted by last_message_at desc, enriched with other_user profile + photo + unread count.
- `GET /conversations/{id}/messages?limit=50&before_id=` returns messages chronological (we fetch desc then reverse). Plus mark as read (update is_read).
- Pagination cursor via `before_id` using created_at < reference.

## Real-time

- Single endpoint `WS /messaging/ws?token=JWT`
- Auth via token query because WS headers tricky.
- On connect: `manager.connect(user_id, websocket)`
- On disconnect: cleanup.
- Client sends no data except ping, server pushes new_message + typing.

- Typing indicator: `POST /conversations/{id}/typing?is_typing=true` -> WS push to other participant.

## Scale Considerations

- **Single node limit**: ~10k WS connections per uvicorn worker (due to Python asyncio). Need 10 nodes for 100k concurrent.
- **Redis PubSub**: Ensure each API node subscribes to `ws:*` channels via asyncio redis client, forwards to local sockets. Use pattern subscribe.
- **Hot partition**: If a celebrity user gets 10k messages/s (unlikely), conversation partitioning would still be hot – but Tinder is peer-to-peer, not fan-out, so OK.
- **Message storage**: For 200M/day, Postgres will struggle beyond few months. Migration path: move messages older than 30 days to S3 + Athena, or switch to ScyllaDB/Cassandra (wide row per conversation, clustering by created_at).

## Message Types

- `text`: plain content
- `image`/`video`: content may be null, media_asset_id must exist, media_url enrichment on read.
- `system`: e.g., "You matched! Say hi" auto-generated.

## Features Implemented

- Reply to message (reply_to_message_id)
- Read receipts (is_read + read_at)
- Unread counts
- Media sharing via pre-uploaded media asset
- Typing indicator realtime
- Conversation created on match automatically

## Future

- Edit/delete messages (soft delete `is_deleted`)
- Reactions (❤️, 😂) – new table `message_reactions`
- Message encryption end-to-end (Signal)
- GIFs via Tenor API
- Voice messages

## Load Test Math

See `scripts/load_test.py`.

- Average 2314 writes/s – feasible with Postgres + pgbouncer.
- Peak 7k writes/s – need 20 Postgres connections + async pool.
- Read 1M DAU * 20 conversation list loads/day = 20M reads/day = 231/s.

Total ~3k QPS Postgres – fine with 20 pool.

If truly 200M, need read replicas for conversations.

## Client Integration (Frontend)

- Chat page polls REST for history, then listens WS for live.
- On WS new_message, appends to list.
- On send, optimistic append + REST POST.
- Unread badge cleared when opening chat (marks read).

