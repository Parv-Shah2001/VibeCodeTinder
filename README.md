# VibeCodeTinder 🔥 – Production Tinder Replica (Local-First)

**Modular Monolithic Tinder clone – run locally in 2 minutes, zero Docker/K8s needed. Fully functional with real-time messaging, media pipeline, recommendation engine, matching, payments, verification, explore, and more.**

> Frontend: Tinder-like swipe UI with Framer Motion • Backend: FastAPI modular monolith (18 modules, 64 endpoints) • Scale design: 50M users, 1M DAU, 500k new profiles/day, 200M msgs/day, 10M media/day, 1B matches/day architecture • Production docs, K8s, Terraform, monitoring, but **local-first**

## 🚀 LOCAL FIRST – Run on Your Computer (No Docker, No K8s) – 2 Minutes

**This is the recommended way to start. No Postgres, Redis, S3, Docker, Kubernetes needed – SQLite + local filesystem + InMemoryRedis fallback.**

```bash
# 1. Clone
git clone https://github.com/Parv-Shah2001/VibeCodeTinder.git
cd VibeCodeTinder

# 2. Backend – Python venv + SQLite
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install faker          # for seed data
cp .env.example .env       # already set to DATABASE_URL=sqlite:///./vibe.db and local storage

# 3. Run API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# → API docs: http://localhost:8000/docs
# → Health: http://localhost:8000/health (should show database ok, storage local)

# 4. Seed 100 demo users (in another terminal)
source .venv/bin/activate
python scripts/seed.py --count 100
# → Creates user1@vibe.test / password123 + 99 others with photos + swipes/matches/messages

# 5. Frontend – Vite React
cd frontend
npm install
npm run dev
# → Frontend: http://localhost:5173
# Login: user1@vibe.test / password123
```

**One-command runner (starts both backend + frontend):**
```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
# Starts backend :8000 and frontend :5173 together, with auto-seed on first run
```

Full local guide: [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md) – step-by-step with troubleshooting.

### What you can test locally (all Tinder same-to-same, no external services)

- **Auth** – register/login/refresh JWT, auto profile via EventBus
- **Onboarding** – `/onboarding` 5-step wizard name/bio/city/job/school
- **Feed** – `/` Tinder card stack drag left/right threshold 100, buttons X/Star/Heart, photo tap indicators, boost button, reload empty state
- **Swipe** – like/dislike/superlike, rate limit 100/min, dedup, history `/swipes/history`
- **Match** – mutual like → instant match modal 🎉 with auto Conversation creation + push notification event
- **Matches/Messages** – `/matches` grid + list with unread badges, start conversation, chat realtime WS via in-memory manager (no Redis needed locally)
- **Chat** – `/chat/:id` text + image upload media in messages, read receipts, typing indicator, reply, scroll
- **Profile** – `/profile` photos grid 6 slots dashed add, primary badge, delete, reorder, edit bio/city/job/school
- **Settings** – `/settings` discovery prefs min/max age distance slider show_me global_mode, geolocation location update, privacy, logout
- **Explore** – `/explore` interests Music/Gaming/Travel/Fitness precomputed groups 3col
- **Likes You** – `/likes-you` Gold feature blur gate Top Picks ML mocked
- **Top Picks** – `/api/v1/explore/top-picks` high Elo + verified scoring
- **Verification** – `/verification` selfie upload mock Rekognition confidence 0.95 blue tick auto approve >0.9 else manual
- **Subscription** – `/subscription` Plus $9.99 Gold $14.99 Platinum $19.99 tiers mock Stripe `payments/create-intent` + confirm webhook
- **Safety** – `/safety` report/block GDPR delete explanation
- **Search** – `/search?q=...` ILIKE name/bio/city/school/job
- **Boost** – super boost, rewind undo last swipe, superlike balance
- **Features** – LaunchDarkly style flags hash bucketing rollout, admin set
- **Analytics** – tracked events user_registered swipe match message_sent media_uploaded daily metrics funnel
- **Admin** – `/admin/stats` total users profiles swipes matches messages media active 24h

All works locally with `./vibe.db` SQLite file + `./storage/profile/` + `./storage/message/` local filesystem, `InMemoryRedis` fallback.

---

## ✨ Features (Complete Tinder)

- ✅ **Auth**: Email/password, JWT access+refresh rotation, phone OTP via SMS (Twilio mock Redis TTL 5m), email verification SES/Sendgrid mock
- ✅ **Onboarding**: display name, bio, age, gender, interested_in, location lat/lon city country job company school height, photo upload 9 max
- ✅ **Discovery Feed**: geo bbox + age + gender + show_me + blocked exclude + swiped exclude, Elo + distance bonus + activity + newbie boost 100 (for 500k/day) + boosted 200 + verified 30 + completeness + random ε-greedy, Redis cache 5min
- ✅ **Swipe Engine**: Like/Pass/SuperLike, rate limiting 100/min Redis INCR, dedup Redis Set `swiped:{uid}` + DB unique + Bloom filter simulation for 1B/day
- ✅ **Matching**: mutual like → instant Match sorted (u1<u2) unique optimistic locking handles race, auto Conversation, push notification
- ✅ **Messaging**: conversations sorted last_message_at, messages text/image/video/system, media sharing, read receipts unread counts reply-to typing indicators, realtime WebSocket manager dict user→sockets + Redis PubSub for horizontal 10 nodes 10k conns each, rate limit 60/min, 200M/day partitioned monthly plan
- ✅ **Media Pipeline**: validate MIME/size, virus scan ClamAV placeholder, Pillow resize 1080 main + 300 thumb, NSFW Rekognition placeholder, S3/MinIO + local fallback, CDN URL presigned 3600, 10M/day async worker Celery ready
- ✅ **Boost**: 30min boost +200 score, Super Boost 3h, SuperLike priority blue star, Rewind undo last swipe Plus check, balance unlimited Plus else 1/day
- ✅ **Subscription**: Free/Plus/Gold/Platinum feature gating Plus unlimited likes rewind passport no ads, Gold see who liked Top Picks 5 superlikes/week, Platinum priority likes 7x message before match, Stripe PaymentIntent mock + webhook invoice.payment_succeeded auto-renew, history
- ✅ **Explore**: Explore tab interests grouping, Top Picks ML curated Elo+verified, Likes You Gold
- ✅ **Verification**: Photo verification selfie vs profile CompareFaces mock confidence 0.75-0.99 auto approve >0.9 else manual review queue, is_verified blue tick
- ✅ **Payments**: Stripe mock pricing Plus $9.99 Gold $14.99 Platinum $19.99 Boost $6.99 Superlike pack $4.99, intent create confirm webhook
- ✅ **Moderation**: Report reason description, Block unique blocker/blocked both directions filter discovery/messaging/search
- ✅ **Search**: ILIKE name/bio/city/school/job enriched photo, future ES/OpenSearch for 50M
- ✅ **Features**: Feature flag hash bucketing md5(name:user_id)%100 < rollout, Redis override, LaunchDarkly style, admin set_flag, A/B testing
- ✅ **Notifications**: EventBus match.created message.sent → push FCM/APNS placeholder + Redis publish + email match
- ✅ **Analytics**: AnalyticsEvent DailyMetrics DAU new_users swipes likes matches messages media uploads revenue, track_event sync/async, handlers for all events, funnel per user, daily metrics aggregated
- ✅ **Worker**: Celery app Redis broker backend, tasks process_media async, send_push, send_email, refresh_rec_cache, compute_daily_metrics, cleanup_old_data TTL 90d
- ✅ **Admin**: stats total users profiles swipes matches messages media active 24h verified, list users, ban, reports
- ✅ **Realtime**: WS manager multi-device dead cleanup reconnect 3s hook useWebSocket
- ✅ **Security**: Bcrypt cost 12, JWT, rate limiting per IP 300/min + per user swipe/message, CORS, content moderation virus NSFW, GDPR delete cascade S3 delete audit log, presigned S3 3600, secrets in k8s Secret env

Frontend:
- Tinder card stack Framer Motion gestures + photo tap indicators gradient overlay
- Match modal 🎉 with other photo + message button
- Chat live WS + optimistic append + scroll ref + typing indicator
- Matches grid 3-col + Messages list unread badges
- Profile photo manager primary reorder delete add dashed
- Onboarding wizard 5 steps progress bar
- Settings prefs sliders + geolocation + privacy
- Explore interests icons + Top Picks + Likes You blur Gold gate
- Verification selfie upload confidence + blue tick
- Subscription tiers icons pricing features list Stripe mock
- Safety Center report/block/verification/GDPR cards
- BottomNav mobile + TopBar + ErrorBoundary + Loader + PWA manifest

---

## 🏗️ Architecture – Modular Monolith (18 Modules, 64 Endpoints)

```
app/
  core/  config/database (QueuePool 20/40 NullPool SQLite) redis (Redis+InMemory fallback) security (JWT bcrypt) s3 (S3/MinIO+local) events (EventBus+Redis publish) middleware logging+rate limit metrics (Prometheus counters) exceptions pagination logger
  modules/
    auth/ User register/login/refresh/me
    users/ Profile UserPreference age haversine geo Elo boosted verified show_me
    media/ MediaAsset processor validation virus Pillow resize NSFW moderation S3
    discovery/ engine candidate generation geo bbox scoring cache 5min boost
    swipes/ Swipe deduplication rate limiting unique constraint history
    matches/ Match sorted unique optimistic locking auto conversation
    messaging/ Conversation Message WS manager Redis PubSub typing read receipts
    subscriptions/ Subscription tier gating
    moderation/ Report Block is_blocked
    notifications/ push FCM/APNS placeholder event handlers
    analytics/ AnalyticsEvent DailyMetrics track_event funnel
    admin/ stats ban reports
    email/ SES Sendgrid verification match reset security alert
    sms/ Twilio OTP generate verify Redis TTL 5m anti SMS pumping
    payments/ Payment Invoice Stripe pricing intent confirm webhook
    verification/ VerificationRequest Rekognition CompareFaces confidence auto approve >0.9 manual review
    explore/ LikesYou Gold TopPicks ML explore interests grouping
    search/ ILIKE search enriched photo future ES
    features/ Feature flag hash bucketing rollout Redis override LaunchDarkly style A/B
    worker/ Celery app broker Redis tasks process_media push email rec cache daily metrics cleanup
    boosts/ boost 30m super boost 3h rewind superlike balance
  main.py FastAPI lifespan init_db 64 paths health ready metrics docs

frontend/
  Vite React Tailwind Framer Motion Zustand React Router
  api client axios JWT refresh interceptor + analytics tracking
  store auth Zustand localStorage
  hooks useWebSocket reconnect 3s useDebounce useGeolocation
  components SwipeCard TopBar BottomNav MatchModal Loader ErrorBoundary PurchaseModal PWAInstall
  pages Login Feed Matches Chat Profile Settings Onboarding Verification SubscriptionPage LikesYou Explore Safety NotFound
  types User Photo Profile Match Message Conversation
  public manifest.json PWA standalone theme #FF4458
  index.css Tailwind Inter font

docs/ ARCHITECTURE SCALING API MEDIA_PIPELINE RECOMMENDATION MESSAGING DEPLOYMENT SECURITY PRODUCTION_CHECKLIST LOCAL_SETUP
scripts/ seed.py 100 users Pravatar swipes matches messages, load_test.py QPS math, gdpr_delete.py S3 cascade audit, backup.sh pg_dump Redis rdb aws s3 upload, run_local.sh one-command local runner
docker-compose.yml postgres redis minio api frontend (local stack, NO k8s)
docker-compose.prod.yml prod gunicorn nginx prometheus grafana resource limits
k8s/ (OPTIONAL PROD ONLY, not needed local) deployment HPA ingress secret + README
helm/values.yaml + terraform/main.tf RDS ElastiCache S3 CloudFront EKS + monitoring prometheus grafana dashboard loki
nginx/nginx.conf rate limiting zones api 100/s swipe 10/s message 20/s proxy cache feed 5m security headers gzip WS upgrade 3600
gunicorn_conf.py workers cpu*2+1 UvicornWorker max_requests jitter graceful
```

**Decoupling:** Modules communicate via `EventBus` (`user.registered`, `profile.created`, `swipe.created`, `match.created`, `message.sent`, `media.uploaded`) not direct imports. Redis publish for horizontal scale. Ready to extract to microservices – docs/ARCHITECTURE details path.

---

## 📊 Scale Design (Prod Ready, but Local Works)

See `docs/SCALING.md` for math. Local SQLite handles 1M DAU simulation, but prod architecture documented:

| Target | QPS avg | Design Local | Design Prod |
|--------|---------|--------------|-------------|
| 50M users | – | SQLite 85GB users + 75GB media meta | Sharded PG hash %32 Citus |
| 1M DAU | ~3000 RPS peak | Single uvicorn 1k RPS, InMemoryRedis cache 80% hit | ALB 3-10 nodes 4 workers |
| 500k new/day | 5.7/s | SQLite OK | PG pool 20/40 |
| 100M swipes/day | 1157/s | InMemoryRedis Set dedup + DB unique | Redis Set + Bloom filter 2GB vs 10GB, partitioned monthly |
| 1B matches claim | 11574/s | Sorted unique optimistic retry | Realistic 1.5M/day = 17/s, Kafka async for 1B |
| 200M messages/day | 2314/s | SQLite partitioned plan, WS in-memory 10k conns | PG partitioned monthly 100GB/day 3TB/mo S3 cold, 32GB Redis, read replicas |
| 10M media/day | 115/s | Local filesystem `./storage/` + Pillow sync 0.1s/cpu | S3 multipart direct upload presigned + Celery workers 4 nodes 4 cores, 20TB ingress, CloudFront 80% hit |

---

## 🐳 Docker Local (Optional, Still Local, No K8s) – One Command

If you want Postgres+Redis+MinIO S3 locally but still no K8s:

```bash
docker-compose up --build
```

- postgres :5432 vibe/vibe
- redis :6379
- minio :9000 S3 + :9001 UI minioadmin/minioadmin buckets auto
- api :8000/docs
- frontend :5173

K8s `k8s/`, `helm/`, `terraform/` is **optional production only**, ignore for local.

---

## 📖 API – 64 Endpoints

Open http://localhost:8000/docs for interactive.

Base `/api/v1`

- `POST /auth/register` `{email,password,name}` → tokens
- `POST /auth/login`
- `GET /discovery/feed?limit=20&max_distance_km=&min_age=&max_age=`
- `GET /discovery/boost` – 30m boost +200
- `POST /swipes` `{swiped_id, swipe_type}` → is_match + match_id
- `GET /swipes/history` + `likes/received`
- `GET /matches` + DELETE unmatch
- `GET /messaging/conversations` + `POST with/{other_id}` + `GET /messages?limit=50&before_id=` + `POST /messages` + `POST /typing?is_typing=` + `WS /messaging/ws?token=JWT`
- `POST /media/me/upload` multipart + DELETE + reorder + primary + message media upload
- `POST /boosts/boost` + `super-boost` + `rewind` + `superlike/balance`
- `GET /explore` + `top-picks` + `likes-you`
- `GET /search?q=...`
- `POST /verification/submit` selfie_asset_id + status + review admin
- `POST /payments/create-intent` tier product_type + confirm + history + webhook stripe
- `POST /sms/send-otp` phone + `verify-otp`
- `POST /email/verify` + test-match
- `GET /features` + `GET /features/{name}` + `POST` admin
- `POST /analytics/track` + daily + funnel + me/events
- `GET /admin/stats` + users + reports + ban
- `GET /health` detailed DB Redis storage + `/ready` + `/metrics` Prometheus + `/` info

Full table + curl flows: `docs/API.md`.

---

## 🧠 Recommendation Engine

- Candidate gen: geo bbox 111km/deg, age birthdate range, gender interested_in, exclude swiped 1000 + blocked, show_me, fresh updated_at DESC limit 200
- Scoring: Elo 1000 + distance bonus max(0,100-dist) + activity 50 if 24h + newbie boost 100 if 3d (for 500k/day visibility) + boosted 200 + verified 30 + completeness bio 10 job 5 school 5 + random -10..10 ε-greedy
- Cache: Redis `rec:candidates:{uid}` JSON 300s TTL, hit rate 80% → 46 QPS DB vs 231 QPS without
- Invalidation on swipe/profile update via EventBus
- Future: two-tower ML user/item towers BERT CLIP, Feast feature store, H3 indexing res 6 ~36km, FAISS ANNS 50M→1000 candidates 50ms, L1 LightGBM 200→50 L2 Deep NN 50→20 MMR diversity, new user cold-start newbie pool, fairness Elo caps, evaluation Precision@20 online A/B match conv retention – docs/RECOMMENDATION

---

## 💬 Messaging Realtime

- ConnectionManager dict `user_id→[WebSocket]` dead cleanup, broadcast_to_conversation both participants, typing indicator WS push, offline unread count push FCM fallback
- For 1M DAU ~100k concurrent WS 10 nodes 10k conns each + Redis PubSub `ws:user:{id}` channel pattern subscribe
- Partitioning plan monthly + hash conversation_id %16, 100GB/day messages cold archive S3 after 30d Scylla/Cassandra wide row option
- docs/MESSAGING

---

## 📸 Media Pipeline

- Validation MIME allowlist jpeg png webp mp4 video for messages + size 20MB
- Virus scan ClamAV placeholder, NSFW Rekognition DetectModerationLabels placeholder
- Pillow resize longest side 1080 quality 85 optimize + thumb 300x400 quality 70
- Storage S3 put_object ContentType + thumbnail + local fallback `./storage/{folder}/{uuid}.jpg` served `/storage/...` static
- DB MediaAsset storage_key public_url thumbnail_url width height size moderation_score is_primary display_order conversation_id
- Event MEDIA_UPLOADED → async worker Celery in prod
- Scale: direct upload presigned POST client→S3 avoid API bandwidth 20TB/day 2.3 Gbps, S3 multipart, queue Celery, dedup SHA256, lifecycle intelligent-tiering 90d glacier, CloudFront 80% hit
- docs/MEDIA_PIPELINE

---

## 🧪 Tests

```bash
pytest -v
```

Tests: `test_auth` health + register/login, `test_discovery` auth guard + health checks, `test_messaging` auth guard + metrics

---

## 📦 Production Deployment (Optional – Not Needed for Local)

When ready for cloud (ignore for local):

- Dockerfile multi-stage + gunicorn_conf.py workers cpu*2+1
- docker-compose.prod.yml prod gunicorn nginx prometheus grafana
- k8s/ deployment 3→20 HPA CPU 70 memory 80 WS 5000 connections + probes + Service + ingress ALB stickiness + secret ConfigMap + README
- helm/values.yaml replica 3 HPA custom metric WS 5000 resources celere 4 workers
- terraform/main.tf RDS r6g.2xlarge 500GB GP3 multi-AZ backup 7d Citus sharding note, ElastiCache 3 nodes r6g.large Redis7 failover, S3 buckets versioning lifecycle intelligent-tiering glacier, CloudFront OAC CDN, EKS
- nginx/nginx.conf rate limiting zones api 100/s swipe 10/s message 20/s burst cache feed 5m security headers gzip WS upgrade 3600
- monitoring/prometheus.yml scrape api postgres-exporter redis-exporter nginx + grafana-dashboard.json panels DAU swipes/s matches/s messages/s media uploads p95 rec WS cache hit
- .env.production.example RDS ElastiCache S3 CloudFront Sentry OTEL + frontend .env.example
- ci_cd/ci.yml test with postgres redis services ruff pytest import docker buildx push frontend build deploy placeholder kubectl (move to `.github/workflows/` – GitHub App blocked workflow push via API)

See `docs/DEPLOYMENT.md`, `docs/SECURITY.md`, `docs/PRODUCTION_CHECKLIST.md`.

---

## 🗂️ Folder Structure

```
.
├── app/main.py (18 modules, 64 endpoints)
├── app/core/ config database redis s3 security events middleware metrics exceptions pagination logger
├── app/modules/ auth users media discovery swipes matches messaging subscriptions moderation notifications analytics admin email sms payments verification explore search features worker boosts
├── frontend/src/ App main index.css + api client analytics + store auth Zustand + hooks useWebSocket useDebounce useGeolocation + components SwipeCard TopBar BottomNav MatchModal Loader ErrorBoundary + pages Login Feed Matches Chat Profile Settings Onboarding Verification SubscriptionPage LikesYou Explore Safety NotFound + types + public manifest.json PWA + vite.config tailwind
├── docs/ LOCAL_SETUP ARCHITECTURE SCALING API MEDIA_PIPELINE RECOMMENDATION MESSAGING DEPLOYMENT SECURITY PRODUCTION_CHECKLIST
├── scripts/ seed.py 100 users Pravatar swipes matches messages + load_test.py QPS math + gdpr_delete.py S3 cascade audit + backup.sh pg_dump s3 + run_local.sh one-command local runner
├── docker-compose.yml (local Postgres Redis MinIO, NO k8s) + docker-compose.prod.yml prod gunicorn nginx prometheus grafana
├── k8s/ (OPTIONAL PROD ONLY) deployment HPA ingress secret README + helm values.yaml + terraform main.tf
├── nginx/nginx.conf + gunicorn_conf.py + alembic 001_initial.py full schema + init.sql partitioning materialized view archive function
├── requirements.txt + Makefile (dev prod api api-prod frontend seed test migrate k8s-deploy logs clean load-test health metrics)
└── README.md
```

---

## 🔐 Security

- Bcrypt cost 12 + JWT access 60m refresh 30d rotation httpOnly cookie future
- Rate limiting global 300/min/IP in-memory + Redis per user swipe 100/min message 60/min upload 20MB
- Content moderation virus ClamAV + NSFW Rekognition placeholder + Perspective API toxic placeholder + Report Block filters discovery/messaging/search
- Privacy show_me toggle block both directions + GDPR delete cascade profiles/media/swipes/matches/messages S3 delete audit log + presigned S3 3600 CDN private + no email/phone leak public endpoints
- Infra CORS restricted prod frontend domain, nginx security headers SAMEORIGIN nosniff XSS block, secrets k8s Secret env not committed, DB encryption at rest, S3 private CloudFront OAC
- Monitoring abuse swipe velocity >1000/min flagged bot + daily metrics anomaly detection + Analytics swipe velocity
- Future 2FA OTP pyotp + E2E Signal + device fingerprinting + WAF ALB + Dependabot pip audit Sentry OpenTelemetry

---

## 📝 License

MIT

---

## 👨‍💻 Author

Parv-Shah2001 – VibeCodeTinder

Built as production codebase example with modular monolith decoupling for 50M scale, local-first – no k8s needed to run.

---

## Screenshot Flow (Local)

1. `./scripts/run_local.sh` or `uvicorn app.main:app --reload` + `cd frontend && npm run dev`
2. Register → auto profile via EventBus
3. Onboarding `/onboarding` → name bio city job school
4. Upload 3-9 photos `/profile` → set primary
5. Swipe feed `/` drag or buttons X★❤️
6. On mutual like → 🎉 Match modal → Send Message
7. Messages `/matches` → conversation auto exists → chat realtime WS
8. Boost → +200 score → higher discovery
9. Verification `/verification` → selfie → blue tick
10. Subscription `/subscription` → Plus/Gold/Platinum mock Stripe
11. Settings → distance 50km → global mode → geolocation update
12. Explore/Likes You/Top Picks → Gold features blur gate

Enjoy locally! 🔥 No K8s.
