# Local Setup – Run on Your Computer (No Docker, No K8s)

This is the **recommended first run**. No Kubernetes, no Docker, no Postgres, no Redis, no S3 needed. The app falls back to SQLite + local filesystem + InMemoryRedis.

## Requirements

- Python 3.11+
- Node 18+ / 20+
- Git

Optional (for Docker variant):
- Docker + docker-compose (if you want Postgres/Redis/MinIO local stack)

## 1️⃣ Clone

```bash
git clone https://github.com/Parv-Shah2001/VibeCodeTinder.git
cd VibeCodeTinder
git checkout arena/019f674d-vibecodetinder # this branch with full code
```

## 2️⃣ Backend – Local (SQLite, 30 seconds)

```bash
# Create venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install – minimal prod deps
pip install -r requirements.txt

# Optional for seed faker
pip install faker

# Env – already local-first in .env.example
cp .env.example .env
# .env has:
# DATABASE_URL=sqlite:///./vibe.db
# REDIS_URL=redis://localhost:6379/0 (falls back if no Redis)
# S3_* empty => local ./storage/

# Init DB + run API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- You should see logs like `🚀 VibeCodeTinder starting in development mode`, `📦 DATABASE: SQLite (local)`, `📸 S3: local filesystem fallback`

## 3️⃣ Seed Demo Data (100 users with photos, matches, messages)

In another terminal (same venv):

```bash
source .venv/bin/activate
python scripts/seed.py --count 100
```

Output:
```
Seeding 100 demo users...
Created 100 users
Creating swipes for user1@vibe.test...
Seed complete! Login with user1@vibe.test / password123
```

## 4️⃣ Frontend – Local (Vite)

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

Login:
- **Email:** `user1@vibe.test`
- **Password:** `password123`

### What you can test locally (all Tinder features working)

1. **Login/Register** – JWT auto stored
2. **Onboarding** – go to `/onboarding` first time, create display_name, bio, city, job, school
3. **Feed** – `/` swipe cards drag left/right or buttons X/Star/Heart, photo tap for next, boost button top-right
4. **Match** – swipe like on seeded users, auto match modal 🎉 when mutual like
5. **Matches/Messages** – `/matches` shows matches grid + conversations list with unread badges, start conversation, chat realtime WS (works locally via in-memory manager, no Redis needed)
6. **Chat** – `/chat/:id` send text, image upload (media in messages), typing indicator, read receipts
7. **Profile** – `/profile` upload photos (drag & drop, 9 max), set primary, reorder, delete, edit bio/city/job/school
8. **Settings** – `/settings` discovery prefs min/max age, distance slider, show_me, global_mode, location update (browser geolocation), privacy
9. **Explore** – `/explore` interests Music/Gaming/Travel grouping
10. **Likes You** – `/likes-you` Gold feature mock blur gate
11. **Top Picks** – `/explore/top-picks` via `/api/v1/explore/top-picks`
12. **Verification** – `/verification` selfie upload mock Rekognition confidence 0.95 approved blue tick
13. **Subscription** – `/subscription` tiers Plus $9.99 Gold $14.99 Platinum $19.99 mock Stripe via `/payments/create-intent` + confirm
14. **Safety** – `/safety` report/block GDPR delete explanation
15. **Search** – search bar via `/search?q=...` ILIKE

All without any external services!

## 5️⃣ API Quick Test (curl)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"user1@vibe.test","password":"password123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl http://localhost:8000/api/v1/users/me/profile -H "Authorization: Bearer $TOKEN" | jq

curl http://localhost:8000/api/v1/discovery/feed?limit=5 -H "Authorization: Bearer $TOKEN" | jq

curl -X POST http://localhost:8000/api/v1/swipes -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"swiped_id":2,"swipe_type":"like"}' | jq
```

## 6️⃣ Docker Variant (Optional – Still Local, No K8s)

If you *do* want Postgres + Redis + MinIO S3 locally (closer to prod but still one command, no K8s):

```bash
docker-compose up --build
```

Services:
- postgres :5432 (vibe/vibe)
- redis :6379
- minio :9000 S3 + :9001 UI (minioadmin/minioadmin) – buckets auto-created
- api :8000
- frontend :5173

This uses `docker-compose.yml` not k8s. K8s (`k8s/`, `helm/`, `terraform/`) is **only for production cloud deployment**, ignore for local.

## 7️⃣ Makefile Shortcuts (Local)

```bash
make api          # uvicorn reload :8000
make frontend     # npm dev :5173
make seed         # 100 users
make seed-large   # 1000 users
make test         # pytest
make health       # curl /health
make load-test    # QPS math simulation
```

## 8️⃣ Data – Where is it Stored Locally?

- SQLite file: `./vibe.db` (gitignored)
- Media: `./storage/profile/` and `./storage/message/` – served via FastAPI static at `/storage/...`
- No S3 needed, but if you set S3_* env it will use MinIO/S3
- Redis: InMemory fallback dict if no Redis running – swipe dedup sets, feed cache, rate limits all work in-memory for local

## 9️⃣ Troubleshooting Local

**ModuleNotFoundError: fastapi**
```bash
pip install -r requirements.txt
```

**Email validator error**
```bash
pip install email-validator
```

**Frontend blank**
- Check API running at :8000
- Check `frontend/.env` – `VITE_API_URL=http://localhost:8000/api/v1` (default via vite.config proxy)

**Upload fails**
- Ensure `./storage/` writable: `mkdir -p storage/profile storage/message && chmod 777 storage -R`

**WS not connecting**
- For local, WS uses `ws://localhost:8000/api/v1/messaging/ws?token=...` – via same host, no Redis needed. Works via in-memory manager.

**Seed fails with faker missing**
```bash
pip install faker
```

## 🔟 Next – Production (When Ready, Not Needed Now)

When you want to deploy to cloud (optional, ignore for local):

- `k8s/` – Kubernetes manifests (Deployment HPA Ingress Secret) – 3 replicas → 20 autoscale
- `helm/values.yaml` – Helm chart values
- `terraform/main.tf` – RDS Postgres, ElastiCache Redis 32GB, S3 buckets, CloudFront CDN, EKS
- `docker-compose.prod.yml` – prod stack with gunicorn, nginx, prometheus, grafana
- `nginx/nginx.conf` – rate limiting zones, cache, security headers
- `monitoring/prometheus.yml` + grafana dashboard

But for now: **just run locally with SQLite – zero deps**.

## 11️⃣ Sample Flow Demo Video Script (30 sec)

1. Register → auto profile
2. Onboarding → name bio city job
3. Upload 3 photos → set primary
4. Feed → swipe right 10 times
5. Match modal → click Send Message
6. Chat → send "Hey 👋"
7. Profile → Boost → +200 score
8. Settings → change distance 50km → save
9. Likes You → blurred Gold gate

Enjoy locally! 🔥 No K8s needed.
