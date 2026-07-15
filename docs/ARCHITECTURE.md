# VibeCodeTinder – Architecture

## Overview
**Modular Monolith** – single deployable unit, but code is strictly decoupled by domain modules. Each module owns its models, schemas, service, repository, router, and publishes/subscribes to domain events via internal EventBus (optionally backed by Redis Streams for future scale-out).

This keeps velocity high early while preserving ability to extract microservices later with zero coupling.

## Module Map
```
app/
  core/              # cross-cutting: config, database, redis, security, s3, events, middleware
  modules/
    auth/            # User + JWT + login/register/refresh
    users/           # Profile, preferences, onboarding
    media/           # Upload, processing pipeline, storage abstraction (S3 + local fallback)
    discovery/       # Recommendation engine (candidate gen + scoring)
    swipes/          # Like/dislike/superlike + rate limiting + dedup
    matches/         # Match creation on mutual like, optimistic locking
    messaging/       # Conversations, messages, media in messages, WebSocket realtime
    notifications/   # Push via FCM/APNS placeholder + event listeners
    subscriptions/   # Plus/Gold/Platinum entitlements
    moderation/      # Report & block + NSFW placeholder
```

### Decoupling Rules
- Modules must not import from sibling modules' internals (models/services). Communication via:
  - **EventBus**: `user.registered`, `profile.created`, `swipe.created`, `match.created`, `message.sent`
  - **Repository queries** allowed only when explicitly needed (e.g., matches needs swipes repo to check mutual like) – documented and limited.
- Core never imports from modules.
- Frontend talks only to `app.main` aggregated router.

## Data Flow

### Registration → Profile → Discovery → Swipe → Match → Messaging
1. `POST /auth/register` -> creates User, publishes `USER_REGISTERED`
2. `handle_user_registered` auto-creates Profile -> publishes `PROFILE_CREATED`
3. User uploads photos via `media` – processed and cached.
4. Discovery `GET /discovery/feed`:
   - Loads viewer profile + preferences
   - Gets swiped ids (Redis Set + Postgres)
   - Geo bounding box for fast filter (future: PostGIS or H3)
   - Candidate query (LIMIT 200) -> scoring loop (Elo, distance, boost, verified, recency, newbie boost + random exploration)
   - Returns enriched with photos
   - Redis cache 5min.
5. Swipe `POST /swipes`:
   - Rate limit via Redis INCR per minute
   - Deduplicate via Redis Set `swiped:{user_id}` + DB unique constraint
   - Persist swipe, publish event, check mutual like.
   - If mutual like -> `check_and_create_match` with sorted user1/user2 unique constraint to prevent race; on IntegrityError fetch existing.
   - Auto-creates Conversation.
   - Publish `MATCH_CREATED` -> push notification.
6. Messaging:
   - REST `POST /conversations/:id/messages` persists message + updates conversation last_message_at + match last_message_at for sort.
   - Publishes WS broadcast via `ConnectionManager` (in-memory + Redis publish for horizontal).
   - Client connects `WS /messaging/ws?token=JWT` -> manager holds `user_id -> [sockets]`.
   - Offline: unread count, last_message caching, push fallback.

## Storage

- **Postgres** primary. Tables:
  - `users` – auth
  - `profiles` – denormalized elo, swipe_count etc. Index on elo_score, location (future GiST).
  - `media_assets` – polymorphic owner (user profile vs conversation). Status workflow pending→ready.
  - `swipes` – unique (swiper, swiped) + covering indexes for history. Partition by month at scale.
  - `matches` – unique (user1,user2) sorted. Index last_message_at for feed.
  - `conversations` / `messages` – conversation unique (sorted). Messages indexed (conversation_id, created_at DESC). Partition by month + hash.
  - `subscriptions`, `reports`, `blocks`

- **Redis**:
  - Rate limiting token bucket (simple INCR/window)
  - Swipe dedup Set `swiped:{user_id}`
  - Recommendation cache `rec:candidates:{user_id}` JSON 300s TTL
  - Online presence (could add)
  - PubSub for WS + events

- **S3 / MinIO**:
  - Buckets: `vibe-media` (profile), `vibe-message-media`
  - Upload pipeline: validate → virus scan (placeholder) → resize via Pillow (1080 max + 300 thumb) → NSFW check (placeholder Rekognition) → put_object
  - CDN URL returned. Presigned URL for private.

## Scale Targets & Design Justification

See `SCALING.md` for math.

- 50M users total: Postgres sharded by user_id hash % 32, or use Citus.
- 1M DAU: API needs ~3k RPS peak. Single codebase with 4 gunicorn workers + async can handle ~1k RPS; behind ALB 3 nodes = 3k.
- 500k new profiles/day ~ 5.7/sec – fine for Postgres + S3.
- 1B matches/day claimed is unrealistic (requires > 11k matches/sec, means everyone matches everyone); we architect for 1B *swipes*/day. Match creation path uses sorted unique constraint + retry to avoid double.
- 200M messages/day ~ 2314 msg/s avg, 7k peak. Partition messages table, use async writes, index optimization, unread counter in Redis.
- 10M media uploads/day ~115/sec + thumbnails: S3 multipart, queue processing (could use Celery + SQS). Our sync processing ok for MVP, but note to move to worker.

## Observability
- Structured logging via structlog (JSON).
- Middleware logs request duration.
- Prometheus placeholder (would add FastAPI instrumentator).
- Sentry placeholder.

## Security
- Bcrypt password hash.
- JWT access 60min + refresh 30 days.
- CORS configured.
- Rate limit middleware + per-endpoint redis limits.
- Content moderation pipeline.
- Block filters discovery.

## Future Extraction Path to Microservices
- Discovery service: extracts engine.py + own read replica + feature store + ML model server.
- Media service: standalone worker pool consuming upload jobs.
- Messaging service: separate WS cluster + message store (Scylla/Cassandra for 200M/day).
- Match service: Kafka consumers for swipes topic.
But starting monolithic avoids distributed transactions and keeps strong consistency for MVP.

## Frontend
React Vite SPA mimicking Tinder UI: card stack with framer-motion, 3-card buffer, gestures, match modal, chat with WS live + typing indicators.

