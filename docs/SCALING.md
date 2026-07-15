# Scaling to 50M Users, 1M DAU

## Assumptions & Math

### Users
- 50M total stored, 1M DAU.
- Each user row ~ 1KB + profile ~ 0.5KB + pref 0.2KB = 1.7KB * 50M = 85GB.
- Plus media metadata: avg 3 photos per user (9 max) = 150M rows * 0.5KB = 75GB.
- Total ~ 160GB core DB – fits on single m6g.2xlarge RDS with 500GB GP3.

### New profiles 500k/day
- 5.8 per second average. Peak 3x = 17/s.
- Write QPS trivial for Postgres (can handle 5k write/s). Need connection pooling done via SQLAlchemy QueuePool (20 pool + 40 overflow).

### Swipes 100M/day (100 per DAU)
- 1157 swipes/s avg, 3500 peak.
- Hot path: dedup check -> Redis `SISMEMBER O(1)` + DB insert.
- `swipes` table: 100M rows/day * 90 days retention (or archive to S3). 9B rows 90 days is huge -> must partition & TTL.
- Strategy:
  - PostgreSQL declarative partitioning by range `created_at` monthly.
  - Each partition ~3B rows max still big, so add hash subpartition by swiper_id % 16.
  - Alternative: for 1B swipes/day, move to Scylla/Cassandra with TWCS.

### Matches – claimed 1B/day is likely mis-stated; realistic match rate 1-5%
- If 100M swipes/day and 3% mutual like => 1.5M matches/day (since 2 swipes per match). That's 17 matches/s average, 50 peak.
- Even 1B matches/day = 11574 matches/sec -> needs Kafka serialization.
- Our implementation: sorted (user1<user2) unique constraint + optimistic retry to avoid race. For 11k QPS would need:
  - Insert into Redis Set first (probabilistic), then async persist to DB via outbox.
  - Or use stored procedure with `INSERT ... ON CONFLICT DO NOTHING`.

### Messages 200M/day
- 2314 msg/s avg, 7000 peak write.
- Message row ~ 0.5KB (content + metadata) => 100GB/day, 3TB/month – must not keep all hot. Cold archive to S3 after 30 days, keep recent in hot partition.
- Write pattern: message insert + conversation update last_message_at in same TX.
- Read: conversations list sorted by last_message_at. Index handles 1M DAU scanning 50 convos each => 50M reads/day ~ 578/s.

### Media 10M/day
- Avg size 2MB -> 20TB/day ingress. S3 infinite, but cost. Thumbnails + compression reduce 50%.
- Processing: Pillow resize is CPU. 115 resizes/sec * 0.1 sec CPU each = 11.5 CPU cores needed continuous. So 4 worker nodes with 4 cores each.
- Solution: upload raw to S3 `pending/` bucket, push job to Celery/SQS, worker does processing & moves to final bucket + updates DB.
- CDN: CloudFront 80% hit reduces origin to 4TB/day egress.

## Caching Strategy

- **Recommendation Feed**: Without cache, each feed request does 2 queries (profile + candidate 200). 1M DAU * 20 feeds/day = 20M feed queries/day = 231 QPS. With Redis cache 5 min TTL, hit rate 80% => 46 QPS to DB.
- **Swipe dedup**: Redis Set `swiped:{uid}` – 1M DAU * 1000 entries avg (maybe trimmed to 30 days) = 1B members ~ 10GB if stored as ints (8 bytes) plus overhead -> use Bloom filter (1B entries 1% false positive ~ 1.2GB). Our implementation keeps full Set for MVP but notes Bloom.
- **Online presence**: Redis `online:{uid}` TTL 5 min.

## Redis Sizing

- 1M DAU active connections set + swipe sets + recommendation caches.
- Estimated ~32GB Redis cluster (3 shards).

## Postgres Sharding

- Vertical scaling first up to db.r6g.4xlarge.
- Then Citus or manual hash sharding on user_id.
- Reference tables: profiles, media, swipes, matches, conversations all sharded by user_id (colocated).
- Cross-shard query (discovery) needs scatter-gather + merge.

## Messaging at Scale

- Our WebSocket manager in-memory works for single node ~10k conns.
- For 1M DAU ~100k concurrent WS (10% online at same time), need 10 nodes * 10k.
- Use Redis PubSub to broadcast: when node A sends to user_id on node B, publish to `ws:user:{id}` channel, B's subscriber forwards to local socket.
- Persistence: use WebSocket gateway (Cowboy? Or separate service in Go/Elixir).

## Recommendation Engine Scale

MVP SQL scoring is O(candidate) per request (200 scoring * constant). For 20M requests/day = 4B scoring iterations/day too high.

Production path:
- Offline batch: Spark job generates candidate lists per user daily using feature store (age, location via H3 indexing, gender).
- Store in `rec_candidates` table or Redis sorted set.
- Online ranking: lightweight ML model (two-tower) served via ONNX or TorchServe, latency ~20ms.
- Real-time signals: recent swipe events consumed via Kafka to update user embedding (streaming).

## Media Pipeline Scale

See `MEDIA_PIPELINE.md`.

## Observability & Ops

- Prometheus metrics: request_duration_histogram, swipe_counter, match_counter, message_counter, media_upload_duration.
- Grafana dashboards.
- Paging: if message QPS > 10k, autoscale.
- Tracing: OpenTelemetry.

## Cost Estimate (rough AWS)

- Postgres RDS 4xlarge ~ $1k/mo
- Redis Elasticache 32GB cluster ~ $800
- S3 storage 600TB/mo (if 20TB/day *30) ~ $13k + CDN $5k
- EC2 API 10 nodes c6g.xlarge ~ $1.5k
- WS nodes 10 nodes ~ $1.5k
- Total ~ $23k/mo infra, before ML.

## Conclusion

Modular monolith is sufficient for 1M DAU MVP and can scale to 50M users with partitioning + Redis. Beyond 5M DAU or 500M messages/day, extract messaging & discovery to separate services with Cassandra & feature store.
