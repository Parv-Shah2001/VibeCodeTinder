"""
Load test simulation for scale targets:
- 1M DAU
- 500k new profiles/day
- 200M messages/day ~ 2300 msg/sec
- 10M media uploads/day ~ 115/sec
- 1B swipes/matches/day (simulated)

This script doesn't actually hit 1B, but simulates patterns and prints expected infra sizing.

Run with: python scripts/load_test.py
"""
import time
import random

def estimate_qps(daily):
    return daily / 86400

def main():
    print("=== VibeCodeTinder Scale Simulation ===")
    targets = {
        "DAU": 1_000_000,
        "New Profiles / day": 500_000,
        "Matches / day (claimed)": 1_000_000_000,
        "Messages / day": 200_000_000,
        "Media Uploads / day": 10_000_000,
        "Swipes / day (assume 100 per DAU)": 100_000_000,
    }
    for k,v in targets.items():
        print(f"{k:30} {v:15,}  ~ {estimate_qps(v):.1f} QPS avg, ~ {estimate_qps(v)*3:.1f} QPS peak")

    print("\n--- Infra sizing back-of-envelope ---")
    print("Postgres: 50M users row ~ 2KB => 100GB, plus indexes 50GB. Need sharding after 10M.")
    print("  - User table hash-sharded by id % 32")
    print("  - Messages partitioned by month, 200M msgs/day * 0.5KB = 100GB/day => need TTL + cold storage S3")
    print("  - Media metadata 10M/day => 10M rows/day, need to partition")
    print("Redis: swipe dedup sets 1M DAU * 1000 swiped = 1B entries ~ if bloom filter 2GB; else 10GB")
    print("S3: 10M media * 2MB avg = 20TB/day ingress, 600TB/month. CloudFront cache hit 80% reduces origin")
    print("Recommendation: candidate generation 100M * 100 scoring = 10B ops/day -> need precompute via Spark + feature store")
    print("  - Cache feed in Redis 5 min TTL, hit rate 90% reduces DB to 10M queries/day")
    print("WebSocket: 1M DAU concurrent ~ maybe 100k simultaneous, need 10 pods * 10k connections")
    print("\nIf matches is truly 1B/day, that's 11k matches/sec - need Kafka + match aggregator with optimistic locking.")

if __name__ == "__main__":
    main()
