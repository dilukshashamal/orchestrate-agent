.PHONY: up down logs test restart clean

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose exec backend pytest

restart:
	docker compose restart

clean:
	docker compose down -v
