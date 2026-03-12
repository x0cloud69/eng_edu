.PHONY: help install backend frontend up down

help:
	@echo "eng_edu — 사용 가능 타겟"
	@echo "  make install   - 백엔드/프론트엔드 의존성 설치"
	@echo "  make up        - Docker (Postgres, Redis) 기동"
	@echo "  make down      - Docker 중지"
	@echo "  make backend   - 백엔드 서버 실행 (uvicorn)"
	@echo "  make frontend  - 프론트엔드 개발 서버 실행"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

up:
	docker compose up -d

down:
	docker compose down

backend:
	cd backend && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev
