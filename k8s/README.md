# K8s Production Deployment

## Scale for 50M users
- 3 replicas min, HPA up to 20 based on CPU 70% and WS connections 5k per pod
- Liveness / readiness probes /health /ready
- ALB ingress with stickiness for WebSocket (lb_cookie 24h) and regular HTTP
- Separate WS ingress with 3600s timeout

## Deploy

```bash
kubectl create namespace vibe-prod
kubectl apply -f secret.yaml -n vibe-prod
kubectl apply -f deployment.yaml -n vibe-prod
kubectl apply -f ingress.yaml -n vibe-prod
kubectl get pods -n vibe-prod -w
```

## Secrets
Edit secret.yaml with real RDS, Redis, S3 keys. Or use external-secrets operator with AWS Secrets Manager.

## Monitoring
- Prometheus scrapes /metrics
- Grafana dashboard import: FastAPI + Postgres + Redis
- HPA metric vibe_ws_active_connections requires prometheus-adapter

## Future: Sharding
- Use Citus for PG sharding or Vitess
- Redis Cluster 3 shards 32GB
- Separate node pools: api (c6g.xlarge), ws (r6g.large memory optimized for 10k conns)
```

