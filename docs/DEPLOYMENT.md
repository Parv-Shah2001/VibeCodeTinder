# Deployment Guide

## Local Quick Start (SQLite + local storage, no Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env DATABASE_URL=sqlite:///./vibe.db
uvicorn app.main:app --reload
# Seed
pip install faker
python scripts/seed.py --count 100
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open:
- Frontend http://localhost:5173
- API http://localhost:8000/docs

Login with seeded user: `user1@vibe.test` / `password123`

## Docker Compose (Postgres + Redis + MinIO + API + Frontend)

```bash
docker-compose up --build
```

Services:
- postgres :5432
- redis :6379
- minio :9000 (S3) + :9001 UI (minioadmin/minioadmin)
- api :8000
- frontend :5173

The api service runs migrations automatically via `init_db()` in lifespan.

To create buckets in MinIO: MinIO creates automatically in storage service, but you can check at http://localhost:9001.

## Production Docker

Dockerfile builds single image.
Run with:
```bash
docker build -t vibecodetinder:latest .
docker run -p 8000:8000 --env-file .env vibecodetinder:latest
```

Recommended production command for scale (gunicorn):
```dockerfile
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```
4 workers * threads.

## Environment Variables

See `.env.example`:

- `DATABASE_URL` – Postgres with psycopg2 or SQLite for local.
- `REDIS_URL`
- `S3_*` – for MinIO/AWS. Leave empty for local filesystem fallback.
- `SECRET_KEY` – 32+ chars
- `CORS_ORIGINS`

## Migrations

We use `init_db()` auto-create for dev. For production with Alembic:

```bash
# generate revision
alembic revision --autogenerate -m "initial"

# apply
alembic upgrade head
# or env var DATABASE_URL set
DATABASE_URL=postgresql://... alembic upgrade head
```

## Scaling Deployed System

- **API**: Behind ALB, 3-10 nodes with auto-scaling CPU >70%. Use `uvicorn --workers 4`.
- **Postgres**: RDS m6g.2xlarge, enable read replica for discovery feed. Use pgbouncer.
- **Redis**: Elasticache cluster mode enabled, 3 shards.
- **S3**: buckets with lifecycle: move to Intelligent-Tiering after 90 days.
- **CDN**: CloudFront pointing to S3 media buckets.
- **WS**: Needs sticky sessions or Redis PubSub cluster. ALB with stickiness enabled or separate WS cluster using NLB.
- **Monitoring**: Prometheus + Grafana, Sentry, CloudWatch.

## CI/CD

Suggested GitHub Actions:
```yaml
- build Docker image
- run pytest
- push to ECR
- deploy to ECS/EKS
```

## Storage Directories

`./storage/profile` and `./storage/message` created automatically for local fallback. Git-ignored.

## Seeding Production-like Data

```bash
python scripts/seed.py --count 1000
```

Creates random users with profile photos from Pravatar.

## Load Test

```bash
python scripts/load_test.py
```

Prints back-of-envelope QPS.

## Health Checks

- `/health` returns ok
- `/` returns info
- API docs at `/docs`

## Troubleshooting

- If `psycopg2` missing: `pip install psycopg2-binary`
- If Redis unavailable, fallback to InMemoryRedis works (logs will show).
- If S3 unavailable, fallback to local.
- CORS: set `FRONTEND_URL` correctly.

