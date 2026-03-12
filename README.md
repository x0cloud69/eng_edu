# eng_edu

AI-Native SaaS 표준 프레임워크 기반 프로젝트 구조입니다.

## 디렉터리 구조

```
eng_edu/
├── backend/                 # Python FastAPI
│   ├── src/
│   │   ├── api/             # FastAPI 앱, 라우터, deps
│   │   ├── core/            # config, logging, security, cache, audit, exceptions
│   │   ├── db/               # Base, session, migrations
│   │   ├── models/           # BaseModel, TenantModel
│   │   ├── schemas/          # ApiResponse, PaginatedResponse
│   │   ├── utils/            # datetime, pagination
│   │   └── modules/          # 비즈니스 모듈 (CRUD 등)
│   └── requirements.txt
├── frontend/                 # Next.js + React + TypeScript
│   └── src/
│       ├── app/              # layout, page, providers
│       ├── components/       # common, ui
│       ├── constants/       # api.ts (ENDPOINTS)
│       ├── hooks/            # useAuth, usePagination
│       ├── lib/              # axios, queryClient
│       ├── stores/           # authStore (Zustand)
│       └── types/            # api, auth
├── .env.example
├── docker-compose.yml        # Postgres, Redis
└── Makefile
```

## 실행 방법

1. **환경 변수**: `.env.example`을 복사해 `.env` 생성 후 값 수정
2. **인프라**: `make up` → Postgres, Redis 기동
3. **백엔드**: `make backend` 또는 `cd backend && uvicorn src.api.main:app --reload --port 8000`
4. **프론트엔드**: `make frontend` 또는 `cd frontend && npm install && npm run dev`

## 기술 스택

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2 (async), PostgreSQL, Redis
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, React Query, Zustand
