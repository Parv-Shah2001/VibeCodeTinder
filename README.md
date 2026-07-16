# VibeCodeTinder 🔥 – Production Tinder Replica

**Modular Monolithic Tinder clone built for 50M users scale, fully functional with real-time messaging, media pipeline, recommendation engine, matching, and more.**

> Frontend: Tinder-like swipe UI with Framer Motion • Backend: FastAPI modular monolith • Scale: 1M DAU, 500k new profiles/day, 200M msgs/day, 10M media/day, 1B matches/day architecture

---

## ✨ Features (Same as Tinder)

- ✅ **Auth**: Email/password, JWT access+refresh, auto profile creation
- ✅ **Onboarding**: Display name, bio, age, gender, interested_in, location, job, school, photo upload (9 max)
- ✅ **Discovery Feed**: Geo + age + gender filters, Elo + boost + newbie boost + activity + random exploration scoring, cached in Redis
- ✅ **Swipe Engine**: Like / Pass / SuperLike, rate limiting 100/min, dedup via Redis Set + DB unique constraint, history
- ✅ **Matching**: Mutual like → instant Match creation with optimistic locking (handles 1B/day design), auto Conversation creation, push notifications
- ✅ **Messaging**: Conversations list sorted by last message, text + image/video media, read receipts, unread counts, reply-to, typing indicators, real-time WebSocket + Redis PubSub for horizontal scale
- ✅ **Media Pipeline**: Upload pipeline with validation, virus scan placeholder, Pillow resize (1080 main + 300 thumb), NSFW moderation placeholder, S3/MinIO + local fallback, CDN URL, 10M/day design (async worker ready)
- ✅ **Recommendation Engine**: Candidate generation via geo bounding box (future PostGIS/H3), ranking via Elo + distance + verification + boost + completeness + randomization. Documented path to two-tower ML model.
- ✅ **Boost**: 30 min boost (+200 score)
- ✅ **Subscription**: Free / Plus / Gold / Platinum with feature gating
- ✅ **Moderation**: Report, Block (filters discovery), block list
- ✅ **Notifications**: EventBus listeners for match & message push (FCM/APNS placeholder)
- ✅ **Realtime**: WebSocket manager with multi-device support, typing events, offline queue fallback

Frontend:
- Tinder card stack UI (swipe gestures, photo tap)
- Match modal 🎉
- Chat with live WS
- Matches grid + Messages list
- Profile editor + photo manager (primary, reorder, delete)

---

## 🏗️ Architecture – Modular Monolith

```
app/
  core/              # config, database (SQLAlchemy), redis (fallback InMemory), security (JWT/bcrypt), s3 (S3+local), events (EventBus), middleware
  modules/
    auth/            # User model, register/login/refresh/me
    users/           # Profile + UserPreference, auto-create on USER_REGISTERED event
    media/           # MediaAsset, processor (validate+resize+moderation), service, S3
    discovery/       # engine.py (candidate + scoring), geo.py, service
    swipes/          # Swipe model, dedup, rate limit
    matches/         # Match model, mutual-like check
    messaging/       # Conversation, Message, WS manager, realtime
    notifications/   # push placeholder + event subscriptions
    subscriptions/   # subscription tiers
    moderation/      # report & block
  main.py            # FastAPI app aggregates routers, lifespan init_db, CORS, static

frontend/
  Vite + React + Tailwind + Framer Motion + Zustand
  pages: Login, Feed, Matches, Chat, Profile
  components: SwipeCard, TopBar, MatchModal
  api client with JWT refresh interceptor

docs/                # ARCHITECTURE.md, SCALING.md, API.md, MEDIA_PIPELINE.md, RECOMMENDATION.md, MESSAGING.md, DEPLOYMENT.md
scripts/             # seed.py (100 users with photos), load_test.py (QPS math)
```

**Decoupling:**
- Modules communicate via `EventBus` (`user.registered`, `profile.created`, `swipe.created`, `match.created`, `message.sent`) not direct imports.
- Internal Redis PubSub ready for extraction to microservices.
- `docs/ARCHITECTURE.md` details flow + future microservice path.

### EventBus
```python
event_bus.publish(Events.MATCH_CREATED, {"match_id":..., "user1_id":..., "user2_id":...})
event_bus.subscribe(Events.USER_REGISTERED, handle_user_registered)
```
Optionally publishes JSON to Redis for cross-instance.

---

## 📊 Scale Design

See `docs/SCALING.md` for detailed math.

| Target | QPS avg | Design |
|--------|---------|--------|
| 50M users stored | – | Sharded PG hash user_id %32, Citus |
| 1M DAU | ~3000 RPS peak | ALB 3-10 nodes, 4 workers each |
| 500k new profiles/day | 5.7/s | OK with PG pool 20/40 |
| 100M swipes/day (100 per DAU) | 1157/s | Redis SISMEMBER dedup + partitioned table monthly |
| 1B matches/day (claimed) | 11574/s | Optimistic locking sorted unique + Kafka async (realistic 1.5M matches/day) |
| 200M messages/day | 2314/s | Partitioned monthly, 32GB Redis, read replicas |
| 10M media/day | 115/s | S3 multipart direct upload + Celery workers, 20TB/day ingress |

- **Redis**: swipe dedup Sets, feed cache 5min, rate limiting, WS PubSub.
- **S3**: Media buckets + CloudFront CDN, presigned URLs.
- **Recommendation**: Candidate H3 indexing, FAISS ANNS, two-tower model (documented), offline Spark.
- **WS**: 10k conn per node, 10 nodes for 100k concurrent + Redis PubSub.

---

## 🚀 Quick Start

### Local (SQLite, no Docker)
```bash
pip install -r requirements.txt
cp .env.example .env
# .env DATABASE_URL=sqlite:///./vibe.db
uvicorn app.main:app --reload --port 8000

# seed
pip install faker
python scripts/seed.py --count 100

# frontend
cd frontend
npm install
npm run dev
```
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Login: `user1@vibe.test` / `password123`

### Docker (Postgres+Redis+MinIO+S3)
```bash
docker-compose up --build
```
- API http://localhost:8000/docs
- MinIO UI http://localhost:9001 (minioadmin/minioadmin)
- Frontend http://localhost:5173

### Load test math
```bash
python scripts/load_test.py
```

---

## 📖 API

See `docs/API.md` for full table.

Base `/api/v1`

- `POST /auth/register` `{email,password,name}` → tokens
- `GET /discovery/feed?limit=20`
- `POST /swipes` `{swiped_id, swipe_type}`
- `GET /matches`
- `GET /messaging/conversations` + `/conversations/{id}/messages`
- `WS /messaging/ws?token=JWT`
- `POST /media/me/upload`

Curl example in docs.

---

## 🧠 Recommendation Engine

- **Candidate gen**: geo bbox, age, gender, exclude swiped, exclude blocked, show_me, last 200 fresh.
- **Scoring**: Elo 1000 + distance_bonus + activity + newbie boost 100 (for 500k/day) + boosted 200 + verified 30 + completeness + random.
- **Cache**: Redis 5min.
- Future: two-tower ML, feature store, H3, FAISS.

Details in `docs/RECOMMENDATION.md`.

---

## 💬 Messaging Real-time

- `ConnectionManager` dict user_id → [WebSocket]
- Broadcast on message send via asyncio task + Redis publish
- Typing indicator WS push
- Unread via `is_read=False` count
- Marked read on fetch

See `docs/MESSAGING.md`.

---

## 📸 Media Pipeline

- Validation MIME/size
- Mock virus scan → ClamAV placeholder
- Pillow resize 1080 + thumb 300
- Mock NSFW → Rekognition placeholder
- Storage: S3 (MinIO/AWS) with fallback local `./storage`
- CDN URL, presigned.

See `docs/MEDIA_PIPELINE.md`.

---

## 🧪 Tests

```bash
pytest
```

---

## 📦 Production Deployment

See `docs/DEPLOYMENT.md`:

- Dockerfile multi-stage with gunicorn workers
- docker-compose for local stack
- ENV vars
- Migrations via Alembic
- ALB + autoscale + RDS + Elasticache + S3 + CloudFront + Sentry + Prometheus

---

## 🗂️ Folder Structure

```
.
├── app/main.py
├── app/core/
├── app/modules/*
├── frontend/src/
├── docs/
├── scripts/seed.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔐 Security

- Bcrypt + JWT
- Rate limiting per-IP + per-user Redis
- CORS
- Content moderation + block filter
- Presigned S3 URLs

---

## 📝 License

MIT

---

## 👨‍💻 Author

Parv-Shah2001 – VibeCodeTinder

Built as production codebase example with modular monolith decoupling for 50M scale.

---

## Screenshot Flow

1. Register → profile auto-created
2. Upload 3-9 photos
3. Edit bio/city/job
4. Swipe feed (drag or buttons)
5. On mutual like → 🎉 Match modal
6. Go Messages → conversation auto exists → chat realtime
7. Boost profile → higher discovery

Enjoy! 🔥

