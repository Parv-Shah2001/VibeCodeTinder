# API Documentation

Base URL: `/api/v1`

Interactive docs: `/docs` (Swagger) and `/redoc`

## Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register email/password -> access+refresh |
| POST | /auth/login | Login |
| POST | /auth/refresh | Refresh |
| GET | /auth/me | Current user |

Auth: Bearer JWT via `Authorization: Bearer <access_token>`

## Users / Profiles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users/me/profile | Full profile + photos + preferences |
| POST | /users/me/profile | Create profile |
| PATCH | /users/me/profile | Update profile |
| PATCH | /users/me/preferences | Update discovery prefs (age, distance, show_me) |
| GET | /users/{user_id}/public | Public mini profile |

## Media
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /media/me | List my media |
| POST | /media/me/upload | Upload profile photo (multipart) – processes resize + thumb + moderation |
| DELETE | /media/me/{id} | Delete |
| POST | /media/me/reorder | Body: [ids in order] |
| POST | /media/me/{id}/primary | Set primary |
| POST | /media/messages/{conv_id}/upload | Upload message media |

Limits:
- Max 9 photos per user
- Max 20MB
- Allowed: jpeg, png, webp + video for messages

## Discovery (Recommendation)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /discovery/feed?limit=20&max_distance_km=&min_age=&max_age= | Candidate feed scored |
| GET | /discovery/boost | Boost profile 30min (+200 elo boost) |

Scoring factors documented in `RECOMMENDATION.md`.

## Swipes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /swipes | Body: { swiped_id, swipe_type: like/dislike/superlike } -> returns is_match + match_id |
| GET | /swipes/history | Recent swipes |
| GET | /swipes/likes/received | Who liked me |

Rate limit: 100 swipes/min via Redis.

## Matches
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /matches | List matches with other_user + last_message |
| GET | /matches/{id} | Single match |
| DELETE | /matches/{id} | Unmatch (soft) |

## Messaging
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /messaging/conversations | List conversations with other_user + unread |
| POST | /messaging/conversations/with/{other_id} | Start conversation (requires active match) |
| GET | /messaging/conversations/{id}/messages?limit=50&before_id= | Paginated messages chronological |
| POST | /messaging/conversations/{id}/messages | Send text/media { content, media_asset_id, message_type, reply_to_message_id } |
| POST | /messaging/conversations/{id}/typing?is_typing=true | Typing indicator |
| WS | /messaging/ws?token=JWT | WebSocket for realtime |

WebSocket messages format:
```json
{ "type": "new_message", "conversation_id": 1, "message": {...} }
{ "type": "typing", "conversation_id": 1, "sender_id": 2, "is_typing": true }
```

Rate limit: 60 messages/min.

## Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /subscriptions/me | Current tier |
| POST | /subscriptions/subscribe | { tier: plus/gold/platinum, auto_renew } |

Features gated (logic in Subscription.has_feature):
- plus: unlimited likes, superlike, boost, rewind, passport
- gold: see who liked, top picks
- platinum: priority likes

## Moderation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /moderation/report/{reported_id}?reason=&description= | Report user |
| POST | /moderation/block/{blocked_id} | Block |
| DELETE | /moderation/block/{blocked_id} | Unblock |
| GET | /moderation/blocks | List blocked ids |

Blocking filters discovery & messaging.

## Notifications
| POST | /notifications/test | Test push |

Events `match.created` automatically pushes.

## Health & Misc
| GET | /health | Status |
| GET | / | Info |
| GET | /metrics | Metrics placeholder |
| GET | /storage/... | Local media fallback (dev) |

## Error Format
```json
{ "detail": "Error message" }
```
Status codes: 400 validation, 401 auth, 403 forbidden, 404 not found, 429 rate limited, 500 server.

## Pagination
- Conversations, messages: `limit` + `offset` or `before_id` cursor.
- Discovery: `limit` (1-100)

## Example Flow (curl)
```bash
# register
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{"email":"a@test.com","password":"password123","name":"Alex"}'

# use token
TOKEN=...

curl http://localhost:8000/api/v1/users/me/profile -H "Authorization: Bearer $TOKEN"

# upload photo
curl -X POST http://localhost:8000/api/v1/media/me/upload -H "Authorization: Bearer $TOKEN" -F file=@photo.jpg

# discovery
curl http://localhost:8000/api/v1/discovery/feed?limit=5 -H "Authorization: Bearer $TOKEN"

# swipe
curl -X POST http://localhost:8000/api/v1/swipes -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"swiped_id":2,"swipe_type":"like"}'

# matches
curl http://localhost:8000/api/v1/matches -H "Authorization: Bearer $TOKEN"

# start conv
curl -X POST http://localhost:8000/api/v1/messaging/conversations/with/2 -H "Authorization: Bearer $TOKEN"

# send message
curl -X POST http://localhost:8000/api/v1/messaging/conversations/1/messages -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"content":"Hey!"}'
```
