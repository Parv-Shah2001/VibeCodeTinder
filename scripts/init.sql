-- Initial SQL for Postgres production tuning for 50M users scale
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis"; -- for geo queries if available
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create readonly user for analytics replica
-- CREATE ROLE analytics WITH LOGIN PASSWORD '...';

-- Partitioning setup example for messages (range by month)
-- In production, use declarative partitioning:
-- CREATE TABLE messages_2026_01 PARTITION OF messages FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Indexes for performance (some covered by alembic but ensure)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_profiles_location ON profiles USING GIST (ll_to_earth(latitude, longitude));
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_profiles_elo ON profiles (elo_score DESC);

-- Materialized view for daily metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_active AS
SELECT DATE(created_at) as date, COUNT(DISTINCT user_id) as dau FROM analytics_events WHERE event_type = 'app_open' GROUP BY DATE(created_at);

-- Function to clean old swipes (>90 days) to S3
CREATE OR REPLACE FUNCTION archive_old_swipes() RETURNS void AS $$
BEGIN
  -- In production, copy to S3 via pg_dump or logical replication
  DELETE FROM swipes WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;
