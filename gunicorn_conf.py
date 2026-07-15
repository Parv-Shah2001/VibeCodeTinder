"""
Gunicorn config for production - tuned for 1M DAU, 7k RPS peak
"""
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # e.g., 9 for 4 cpu
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
preload_app = True

# For graceful shutdown
graceful_timeout = 30

# Prometheus metrics: gunicorn prometheus exporter if needed
def when_ready(server):
    print("🚀 VibeCodeTinder Gunicorn ready, workers:", workers)

def worker_int(worker):
    print(f"Worker {worker.pid} received INT")

def on_exit(server):
    print("👋 Gunicorn shutting down")
