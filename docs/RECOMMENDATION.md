# Recommendation Engine

## Goals
- Provide engaging discovery feed
- Surface relevant nearby users based on preferences (age, distance, gender)
- Optimize for matches & conversations (engagement)
- Handle 500k new users/day with newbie boost
- Fairness: not just high Elo users dominate

## Current Implementation (Modular Monolith)

### Candidate Generation (Retrieval)
- Fetch viewer profile + preferences
- Get swiped ids from `swipes` table (last 1000) + Redis Set for dedup.
- Geo filtering: compute bounding box approx (1 deg ~111km) for quick SQL filter. Production would use PostGIS `ST_DWithin` or S2/H3 cell indexing with inverted index.
- Age filter: birthdate range from min_age/max_age.
- Gender filter: `interested_in` vs candidate gender.
- Exclude `show_me=False`
- Query limit `RECOMMENDATION_CANDIDATE_LIMIT*2` (e.g., 200) ordered by `updated_at DESC` to get fresh.

### Scoring (Ranking)
```python
score = elo_score (1000 base)
+ distance_bonus: max(0, 100 - distance_km)
+ activity: +50 if updated last 24h
+ newbie_boost: +100 if created last 3 days (helps 500k new/day get visibility)
+ boosted: +200 if is_boosted
+ verified: +30
+ completeness: bio +10, job +5, school +5
+ random(-10,10) for epsilon-greedy exploration
```

Sorted descending, top `limit` returned.

- Enrich with photos from `media_assets`.
- Cache result JSON in Redis 5 min TTL per user (`rec:candidates:{user_id}`).

### Why this works for MVP
- O(200) scoring per request, cheap (microseconds)
- Epsilon-greedy ensures diversity
- Newbie boost helps onboarding funnel

### Invalidation
- On swipe, cache invalidated via `invalidate_cache(user_id)` or TTL.
- On profile update, publish event to invalidate.

## Production Evolution

### Phase 1: Two-Tower ML Model
- Train on 1B swipes/day historical data.
- User tower features: age, gender, location, bio embeddings (BERT), photo embeddings (CLIP), activity.
- Item tower same.
- Candidate dot product predicts like probability.
- Serve via ONNX Runtime, p95 <20ms.

### Phase 2: Feature Store (Feast)
- Online features in Redis (recent swipes count, elo)
- Offline features in S3/Parquet.

### Phase 3: Retrieval Optimization
- H3 Indexing: earth divided into hexagons res 6 (~36km), retrieve candidates from same + neighboring cells.
- Use Annoy/FAISS index for embedding similarity search across 50M users -> top 1000 candidates in 50ms.
- Apply business rules filter.

### Phase 4: Ranking Stack
- L1: LightGBM 200 features -> prune to 200 candidates to 50.
- L2: Deep NN -> 50 to 20 final ranking with context (time of day, swipe history).
- Diversity re-ranking: MMR to avoid similar profiles.

### New User Problem (500k/day)
- Cold-start: no swipe history, embedding random.
- Solution: newbie pool boost + heuristic (location + popularity) until 10 swipes, then switch to ML.

### Fairness & Safety
- Elo caps to prevent rich-get-richer.
- Blocked users filtered via `get_blocked_ids`.
- Report count down-ranking.

### Evaluation
- Offline: Precision@20, Recall.
- Online A/B: match rate, conversation rate, retention.

### Infrastructure
- Spark job nightly builds candidate index.
- Kafka streams swipe events -> feature store real-time update.
- Model server autoscaled.

## Config
```env
RECOMMENDATION_CANDIDATE_LIMIT=100
RECOMMENDATION_GEO_RADIUS_KM_DEFAULT=50
RECOMMENDATION_CACHE_TTL_SECONDS=300
```

## Future: Superlike Boost
Superlike from viewer should increase chance of being seen by recipient in next feed – implemented as reversed ranking bonus for recipient.

