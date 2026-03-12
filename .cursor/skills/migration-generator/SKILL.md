---
name: migration-generator
description: >-
  Generates an Alembic DB migration file based on a module's models.py.
  Use when the user says "마이그레이션 만들어줘", "DB 테이블 생성", "migration 생성",
  "create migration for XX", "generate alembic migration", or "XX 테이블 추가해줘".
---

# Migration Generator

You are a migration file generator for the AI-Native SaaS Standard Framework.
When the user requests a DB migration, generate an Alembic revision file following the exact patterns below.

## Step 0: Gather Information

Ask the user (if not already provided):
1. **모듈 이름** (snake_case, 예: `esignature`, `payment`, `document`)
2. **테이블 이름** (복수형 snake_case, 예: `e_signature_documents`, `payments`)
3. **비즈니스 필드** — TenantBaseModel 자동 제공 필드 외의 추가 필드

자동으로 확인할 사항:
- `backend/src/modules/{module_name}/models.py` 에서 필드 정보 읽기
- `backend/alembic/versions/` 에서 최신 revision ID 확인

## Step 1: Read models.py

먼저 모듈의 models.py를 읽어서 다음을 파악한다:
- `__tablename__` → 테이블 이름
- 비즈니스 필드 (sa.Column 정의)
- TenantBaseModel 상속 여부 확인

## Step 2: Find Latest Revision

`backend/alembic/versions/` 디렉토리의 기존 마이그레이션에서 최신 revision을 찾는다.

```bash
# 최신 파일 확인
ls -t backend/alembic/versions/*.py | head -1
```

해당 파일의 `revision: str = "..."` 값이 새 마이그레이션의 `down_revision`이 된다.

## Step 3: Generate Migration File

파일 위치: `backend/alembic/versions/{revision_id}_{description}.py`

```python
"""{description}

Revision ID: {new_revision_id}
Revises: {down_revision}
Create Date: {YYYY-MM-DD}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "{new_revision_id}"
down_revision: Union[str, None] = "{down_revision}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "{table_name}",
        # ── 비즈니스 필드 ──
        {business_columns}
        # ── TenantBaseModel 표준 필드 (항상 포함) ──
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
    )
    # ── 인덱스 ──
    op.create_index(
        op.f("ix_{table_name}_tenant_id"),
        "{table_name}",
        ["tenant_id"],
        unique=False,
    )
    {additional_indexes}


def downgrade() -> None:
    {drop_indexes}
    op.drop_index(op.f("ix_{table_name}_tenant_id"), table_name="{table_name}")
    op.drop_table("{table_name}")
```

### Revision ID 생성 규칙

Revision ID는 12자리 hex 문자열로 생성한다:
- 간단한 방식: `e4f5g6h7i8j9` 같은 패턴
- 기존 revision과 충돌하지 않도록 확인

### TenantBaseModel 표준 필드 (항상 포함)

이 필드들은 models.py에서 선언하지 않아도 TenantBaseModel에서 자동 제공되므로, **마이그레이션에서는 반드시 명시적으로 포함**해야 한다:

| 필드 | 타입 | 비고 |
|------|------|------|
| `id` | `UUID(as_uuid=True)` | primary_key=True |
| `tenant_id` | `UUID(as_uuid=True)` | ForeignKey("tenants.id"), nullable=False |
| `created_by` | `UUID(as_uuid=True)` | nullable=True |
| `created_at` | `DateTime(timezone=True)` | nullable=False |
| `updated_at` | `DateTime(timezone=True)` | nullable=False |
| `is_active` | `Boolean()` | nullable=False |
| `is_deleted` | `Boolean()` | nullable=False |
| `deleted_at` | `DateTime(timezone=True)` | nullable=True |

### 필드 타입 매핑

| Python/SQLAlchemy 모델 | Alembic Column |
|------------------------|----------------|
| `Mapped[str]` + `String(N)` | `sa.Column("name", sa.String(N), nullable=False)` |
| `Mapped[Optional[str]]` + `String(N)` | `sa.Column("name", sa.String(N), nullable=True)` |
| `Mapped[int]` | `sa.Column("name", sa.Integer(), nullable=False)` |
| `Mapped[float]` | `sa.Column("name", sa.Float(), nullable=False)` |
| `Mapped[bool]` | `sa.Column("name", sa.Boolean(), nullable=False)` |
| `Mapped[datetime]` | `sa.Column("name", sa.DateTime(timezone=True), nullable=False)` |
| `Mapped[UUID]` | `sa.Column("name", UUID(as_uuid=True), nullable=False)` |
| `server_default="value"` | `server_default="value"` 그대로 전달 |

### 인덱스 규칙

- `tenant_id` 인덱스: **항상 필수** (`ix_{table_name}_tenant_id`)
- `status` 필드가 있으면: 추가 인덱스 (`ix_{table_name}_status`)
- 자주 검색되는 필드: 추가 인덱스 권장
- 인덱스 이름: `ix_{table_name}_{column_name}` 형식

## Step 4: Register Model in db/models.py

`backend/src/db/models.py`에 새 모델을 import하여 Alembic의 autogenerate가 인식하도록 한다:

```python
# 기존 import에 추가
from src.modules.{module_name}.models import {EntityName}  # noqa: F401
```

## Step 5: Verify

생성 완료 후 다음을 확인한다:
1. revision ID가 기존과 충돌하지 않는가
2. down_revision이 최신 revision을 정확히 가리키는가
3. TenantBaseModel 8개 표준 필드가 모두 포함되었는가
4. tenant_id 인덱스가 포함되었는가
5. downgrade()에서 인덱스 → 테이블 순서로 삭제하는가
6. db/models.py에 모델 import가 추가되었는가

## 참고: ALTER TABLE (기존 테이블 수정)

기존 테이블에 컬럼을 추가/수정하는 경우:

```python
def upgrade() -> None:
    op.add_column("{table_name}", sa.Column("{col_name}", sa.String(200), nullable=True))

def downgrade() -> None:
    op.drop_column("{table_name}", "{col_name}")
```

## Reference Files

- `backend/alembic/versions/d3e4f5g6h7i8_add_e_signature_documents.py` — 참조 마이그레이션
- `backend/alembic/env.py` — Alembic 설정
- `backend/src/core/base_model.py` — TenantBaseModel 정의
- `backend/src/db/models.py` — 모델 등록
- `.cursor/context/phase3_context.json` — Phase 3 기준
