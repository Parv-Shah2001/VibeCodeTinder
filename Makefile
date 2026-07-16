.PHONY: dev api frontend seed docker lint test migrate k8s-deploy prod

dev:
	docker-compose up --build

prod:
	docker-compose -f docker-compose.prod.yml up --build -d

api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-prod:
	gunicorn app.main:app -c gunicorn_conf.py

frontend:
	cd frontend && npm install && npm run dev

frontend-build:
	cd frontend && npm install && npm run build

seed:
	python scripts/seed.py --count 100

seed-large:
	python scripts/seed.py --count 1000

lint:
	ruff check app || true
	ruff format --check app || true

test:
	pytest -v --tb=short

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

docker-build:
	docker build -t vibecodetinder:latest .
	docker build -t vibecodetinder:prod -f Dockerfile --target base .

k8s-deploy:
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/ingress.yaml
	kubectl rollout status deployment/vibecodetinder-api

k8s-logs:
	kubectl logs -f deployment/vibecodetinder-api

clean:
	docker-compose down -v
	rm -rf storage/*.db storage/profile storage/message
	rm -rf frontend/dist

load-test:
	python scripts/load_test.py

health:
	curl http://localhost:8000/health | jq

metrics:
	curl http://localhost:8000/metrics
