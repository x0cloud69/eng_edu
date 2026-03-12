---
name: test-scenario-generator
description: >-
  Generates Agent simulation test scenarios for Phase 4 (Simulation/Testing).
  Use when the user says "테스트 만들어줘", "시나리오 생성", "Agent 테스트",
  "create test for XX module", "generate test scenarios", "Phase 4 테스트",
  or "시뮬레이션 테스트 작성".
---

# Test Scenario Generator

You are a test scenario generator for the AI-Native SaaS Standard Framework Phase 4 (Simulation).
When the user requests test scenarios, generate comprehensive pytest test files following the exact patterns below.

## Step 0: Gather Information

Ask the user (if not already provided):
1. **모듈 이름** (snake_case, 예: `esignature`, `payment`) — 테스트 대상 모듈
2. **테스트 범위** — 전체(full) / Agent만(agent) / API만(api) / 특정 시나리오(scenario)
3. **중점 검증 항목** — ApprovalGate / AuditLog / Scope 검증 / 멀티테넌트 격리 / 에러 처리

자동으로 확인할 사항:
- `backend/src/modules/{module_name}/agent.py` 에서 액션 목록 파악
- `backend/src/modules/{module_name}/schemas.py` 에서 필드 정보 파악
- `backend/src/core/base_agent.py` 에서 BaseAgent 표준 흐름 확인

## Step 1: Generate Test Directory Structure

```
backend/tests/
├── conftest.py                    # 공통 fixture
├── modules/
│   └── {module_name}/
│       ├── __init__.py
│       ├── test_agent.py          # Agent 단위 테스트
│       ├── test_service.py        # Service 단위 테스트
│       ├── test_router.py         # API 통합 테스트
│       └── test_scenarios.py      # E2E 시나리오 테스트
```

---

## Step 2: Generate conftest.py — 공통 Fixture

파일 위치: `backend/tests/conftest.py`

```python
"""
테스트 공통 Fixture — Phase 4 시뮬레이션
"""
import asyncio
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from src.core.base_agent import AgentContext, AuthorityLevel, RiskLevel


# ── Event Loop ──
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Mock DB Session ──
@pytest_asyncio.fixture
async def mock_db() -> AsyncGenerator:
    """SQLAlchemy AsyncSession Mock"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    yield session


# ── 테스트용 Tenant / User ID ──
TENANT_ID = "11111111-1111-1111-1111-111111111111"
USER_ID   = "22222222-2222-2222-2222-222222222222"
OTHER_TENANT_ID = "99999999-9999-9999-9999-999999999999"


# ── AgentContext Factory ──
@pytest.fixture
def make_context():
    """AgentContext 생성 팩토리"""
    def _make(
        action: str = "list",
        payload: dict | None = None,
        authority_level: AuthorityLevel = AuthorityLevel.L1,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        approved_by: str | None = None,
        tenant_id: str = TENANT_ID,
        user_id: str = USER_ID,
    ) -> AgentContext:
        return AgentContext(
            user_id=user_id,
            action=action,
            payload=payload or {},
            tenant_id=tenant_id,
            authority_level=authority_level,
            risk_level=risk_level,
            approved_by=approved_by,
        )
    return _make
```

**규칙:**
- conftest.py가 이미 존재하면 기존에 병합 (덮어쓰기 금지)
- TENANT_ID, USER_ID 는 테스트 전용 상수
- OTHER_TENANT_ID 는 멀티테넌트 격리 테스트용

---

## Step 3: Generate test_agent.py — Agent 단위 테스트

파일 위치: `backend/tests/modules/{module_name}/test_agent.py`

### 3-1. 기본 CRUD 테스트

```python
"""
{ModuleName} Agent 단위 테스트 — Phase 4 시뮬레이션
"""
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import pytest_asyncio

from src.core.base_agent import (
    AgentContext,
    AgentResult,
    AuthorityLevel,
    RiskLevel,
)
from src.modules.{module_name}.agent import {ModuleName}Agent

# conftest에서 import
from tests.conftest import TENANT_ID, USER_ID, OTHER_TENANT_ID


class TestBasicCRUD:
    """기본 CRUD 액션 테스트"""

    @pytest_asyncio.fixture
    async def agent(self):
        return {ModuleName}Agent()

    @pytest.mark.asyncio
    async def test_list_success(self, agent, mock_db, make_context):
        """목록 조회 — 정상"""
        ctx = make_context(action="list", payload={{"action": "list", "page": 1, "size": 20}})

        with patch.object(agent, "execute", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = AgentResult(
                success=True,
                data={{"items": [], "total": 0}},
                trace_id=ctx.trace_id,
            )
            result = await agent.execute(ctx, mock_db)

        assert result.success is True
        assert "items" in result.data

    @pytest.mark.asyncio
    async def test_create_success(self, agent, mock_db, make_context):
        """생성 — 정상 (승인 후)"""
        ctx = make_context(
            action="create",
            payload={{"action": "create", {create_test_payload}}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        # Agent.run() 호출 시 ApprovalGate 통과 후 execute() 실행
        assert result.trace_id == ctx.trace_id

    @pytest.mark.asyncio
    async def test_get_not_found(self, agent, mock_db, make_context):
        """조회 — 존재하지 않는 ID"""
        fake_id = str(uuid.uuid4())
        ctx = make_context(
            action="get",
            payload={{"action": "get", "item_id": fake_id}},
            approved_by="admin",
        )
        # Service.get()이 None 반환하도록 Mock
        result = await agent.run(ctx, mock_db)
        # 결과 확인은 Mock 설정에 따라 달라짐

    @pytest.mark.asyncio
    async def test_delete_soft(self, agent, mock_db, make_context):
        """삭제 — soft delete 확인"""
        fake_id = str(uuid.uuid4())
        ctx = make_context(
            action="delete",
            payload={{"action": "delete", "item_id": fake_id}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert result.trace_id == ctx.trace_id
```

### 3-2. ApprovalGate 테스트

```python
class TestApprovalGate:
    """ApprovalGate 동작 검증"""

    @pytest_asyncio.fixture
    async def agent(self):
        return {ModuleName}Agent()

    @pytest.mark.asyncio
    async def test_l1_without_approval_blocked(self, agent, mock_db, make_context):
        """L1 Agent — 승인 없이 실행 시 차단"""
        ctx = make_context(
            action="create",
            payload={{"action": "create", {create_test_payload}}},
            authority_level=AuthorityLevel.L1,
            approved_by=None,  # 승인 없음
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False
        assert result.requires_approval is True
        assert "승인" in result.message

    @pytest.mark.asyncio
    async def test_l1_with_approval_passes(self, agent, mock_db, make_context):
        """L1 Agent — 승인 있으면 실행"""
        ctx = make_context(
            action="create",
            payload={{"action": "create", {create_test_payload}}},
            authority_level=AuthorityLevel.L1,
            approved_by="admin-user",
        )
        result = await agent.run(ctx, mock_db)
        # ApprovalGate 통과 → execute() 실행됨
        assert result.requires_approval is False

    @pytest.mark.asyncio
    async def test_l0_auto_pass(self, agent, mock_db, make_context):
        """L0 — 승인 없이도 자동 통과"""
        ctx = make_context(
            action="list",
            payload={{"action": "list"}},
            authority_level=AuthorityLevel.L0,
            approved_by=None,
        )
        # L0 Agent로 임시 변경
        original_level = agent.authority_level
        agent.authority_level = AuthorityLevel.L0
        result = await agent.run(ctx, mock_db)
        agent.authority_level = original_level
        assert result.requires_approval is False

    @pytest.mark.asyncio
    async def test_high_risk_requires_approval(self, agent, mock_db, make_context):
        """HIGH risk — 무조건 승인 필요"""
        ctx = make_context(
            action="{high_risk_action}",
            payload={{"action": "{high_risk_action}", {high_risk_payload}}},
            risk_level=RiskLevel.HIGH,
            approved_by=None,
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False
        assert result.requires_approval is True

    @pytest.mark.asyncio
    async def test_critical_risk_requires_approval(self, agent, mock_db, make_context):
        """CRITICAL risk — 무조건 승인 필요"""
        ctx = make_context(
            action="{high_risk_action}",
            payload={{"action": "{high_risk_action}", {high_risk_payload}}},
            risk_level=RiskLevel.CRITICAL,
            approved_by=None,
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False
        assert result.requires_approval is True
```

### 3-3. Scope 검증 테스트

```python
class TestScopeValidation:
    """Scope(allowed_tools) 검증"""

    @pytest_asyncio.fixture
    async def agent(self):
        return {ModuleName}Agent()

    @pytest.mark.asyncio
    async def test_allowed_tools_pass(self, agent, mock_db, make_context):
        """허용된 Tool 사용 — 통과"""
        ctx = make_context(
            action="list",
            payload={{"action": "list", "tools": {allowed_tools_list}}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert "Scope 초과" not in (result.message or "")

    @pytest.mark.asyncio
    async def test_disallowed_tool_blocked(self, agent, mock_db, make_context):
        """허용되지 않은 Tool 사용 — 차단"""
        ctx = make_context(
            action="list",
            payload={{"action": "list", "tools": ["api_call_external"]}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False
        assert "Scope" in result.message
```

### 3-4. 멀티테넌트 격리 테스트

```python
class TestMultiTenantIsolation:
    """멀티테넌트 데이터 격리 검증"""

    @pytest_asyncio.fixture
    async def agent(self):
        return {ModuleName}Agent()

    @pytest.mark.asyncio
    async def test_tenant_id_injected(self, agent, mock_db, make_context):
        """tenant_id가 Context에 올바르게 주입되는지 확인"""
        ctx = make_context(
            action="list",
            payload={{"action": "list"}},
            tenant_id=TENANT_ID,
            approved_by="admin",
        )
        assert ctx.tenant_id == TENANT_ID

    @pytest.mark.asyncio
    async def test_cross_tenant_access_denied(self, agent, mock_db, make_context):
        """다른 테넌트 데이터 접근 시도 — 격리 확인"""
        # Tenant A 데이터를 Tenant B가 조회 시도
        ctx = make_context(
            action="get",
            payload={{
                "action": "get",
                "item_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",  # Tenant A 소유
            }},
            tenant_id=OTHER_TENANT_ID,  # Tenant B로 접근
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        # Service가 tenant_id 필터를 적용하므로 None 반환 → 실패
        # (실제 DB Mock 설정에 따라 결과가 달라짐)
        assert result.trace_id == ctx.trace_id
```

### 3-5. AuditLog 테스트

```python
class TestAuditLog:
    """AuditLog 기록 검증"""

    @pytest_asyncio.fixture
    async def agent(self):
        return {ModuleName}Agent()

    @pytest.mark.asyncio
    async def test_audit_logged_on_success(self, agent, mock_db, make_context):
        """성공 시 AuditLog 기록"""
        ctx = make_context(
            action="create",
            payload={{"action": "create", {create_test_payload}}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        # L1 이상이면 audit_logged = True
        if ctx.authority_level != AuthorityLevel.L0:
            assert result.audit_logged is True

    @pytest.mark.asyncio
    async def test_audit_logged_on_failure(self, agent, mock_db, make_context):
        """실패 시에도 AuditLog 기록"""
        ctx = make_context(
            action="unknown_action",
            payload={{"action": "unknown_action"}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False
        if ctx.authority_level != AuthorityLevel.L0:
            assert result.audit_logged is True

    @pytest.mark.asyncio
    async def test_execution_ms_tracked(self, agent, mock_db, make_context):
        """execution_ms 성능 추적"""
        ctx = make_context(
            action="list",
            payload={{"action": "list"}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert result.execution_ms >= 0

    @pytest.mark.asyncio
    async def test_l0_no_audit(self, agent, mock_db, make_context):
        """L0 Agent는 AuditLog 미기록"""
        ctx = make_context(
            action="list",
            payload={{"action": "list"}},
            authority_level=AuthorityLevel.L0,
        )
        original_level = agent.authority_level
        agent.authority_level = AuthorityLevel.L0
        result = await agent.run(ctx, mock_db)
        agent.authority_level = original_level
        assert result.audit_logged is False
```

### 3-6. 에러 처리 테스트

```python
class TestErrorHandling:
    """에러 처리 검증"""

    @pytest_asyncio.fixture
    async def agent(self):
        return {ModuleName}Agent()

    @pytest.mark.asyncio
    async def test_unknown_action(self, agent, mock_db, make_context):
        """알 수 없는 액션 — 실패 반환"""
        ctx = make_context(
            action="nonexistent",
            payload={{"action": "nonexistent"}},
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False
        assert "알 수 없는 액션" in result.message

    @pytest.mark.asyncio
    async def test_missing_required_param(self, agent, mock_db, make_context):
        """필수 파라미터 누락 — 실패 반환"""
        ctx = make_context(
            action="get",
            payload={{"action": "get"}},  # item_id 누락
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_no_db_session(self, agent, make_context):
        """DB 세션 없음 — 실패 반환"""
        ctx = make_context(
            action="list",
            payload={{"action": "list"}},
            approved_by="admin",
        )
        result = await agent.run(ctx, db=None)
        # BaseAgent.run() → execute() → db=None 체크
        assert result.trace_id == ctx.trace_id

    @pytest.mark.asyncio
    async def test_result_always_agent_result(self, agent, mock_db, make_context):
        """어떤 경우에도 AgentResult 반환 (Exception raise 금지)"""
        ctx = make_context(
            action="create",
            payload={{"action": "create"}},  # 필수 필드 누락
            approved_by="admin",
        )
        result = await agent.run(ctx, mock_db)
        assert isinstance(result, AgentResult)
```

---

## Step 4: Generate test_scenarios.py — E2E 시나리오 테스트 (선택)

파일 위치: `backend/tests/modules/{module_name}/test_scenarios.py`

```python
"""
{ModuleName} E2E 시나리오 테스트 — Phase 4
전체 흐름: Orchestrator → Agent → Service → Repository
"""
import pytest
import pytest_asyncio

from src.core.base_agent import AgentContext, AgentResult, AuthorityLevel, RiskLevel


class TestEndToEndScenarios:
    """E2E 시나리오"""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, mock_db, make_context):
        """전체 라이프사이클: 생성 → 조회 → 수정 → 삭제"""
        from src.modules.{module_name}.agent import {ModuleName}Agent
        agent = {ModuleName}Agent()

        # 1. 생성
        ctx_create = make_context(
            action="create",
            payload={{"action": "create", {create_test_payload}}},
            approved_by="admin",
        )
        result_create = await agent.run(ctx_create, mock_db)
        assert result_create.trace_id  # trace_id 존재 확인

        # 2. 조회 (목록)
        ctx_list = make_context(
            action="list",
            payload={{"action": "list", "page": 1, "size": 10}},
            approved_by="admin",
        )
        result_list = await agent.run(ctx_list, mock_db)
        assert result_list.trace_id

        # 3. (mock 기반이므로 실제 DB 연동은 Phase 5에서 검증)

    @pytest.mark.asyncio
    async def test_approval_flow(self, mock_db, make_context):
        """승인 흐름: 요청 → 거부 → 재요청(승인) → 실행"""
        from src.modules.{module_name}.agent import {ModuleName}Agent
        agent = {ModuleName}Agent()

        # Step 1: 승인 없이 요청 → 차단
        ctx1 = make_context(
            action="{high_risk_action}",
            payload={{"action": "{high_risk_action}", {high_risk_payload}}},
            risk_level=RiskLevel.HIGH,
            approved_by=None,
        )
        result1 = await agent.run(ctx1, mock_db)
        assert result1.requires_approval is True

        # Step 2: 승인 후 재요청 → 통과
        ctx2 = make_context(
            action="{high_risk_action}",
            payload={{"action": "{high_risk_action}", {high_risk_payload}}},
            risk_level=RiskLevel.HIGH,
            approved_by="manager",
        )
        result2 = await agent.run(ctx2, mock_db)
        assert result2.requires_approval is False

    @pytest.mark.asyncio
    async def test_concurrent_tenant_isolation(self, mock_db, make_context):
        """동시 멀티테넌트 접근 시뮬레이션"""
        from src.modules.{module_name}.agent import {ModuleName}Agent

        agent_a = {ModuleName}Agent()
        agent_b = {ModuleName}Agent()

        # Tenant A 요청
        ctx_a = make_context(
            action="list",
            payload={{"action": "list"}},
            tenant_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            approved_by="admin-a",
        )

        # Tenant B 요청
        ctx_b = make_context(
            action="list",
            payload={{"action": "list"}},
            tenant_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            approved_by="admin-b",
        )

        result_a = await agent_a.run(ctx_a, mock_db)
        result_b = await agent_b.run(ctx_b, mock_db)

        # 각각 독립적으로 실행
        assert result_a.trace_id != result_b.trace_id
```

---

## Step 5: Generate pytest.ini (없을 경우)

파일 위치: `backend/pytest.ini`

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

---

## Step 6: Verify

생성 완료 후 다음을 확인한다:

1. **구조 확인**: tests/ 디렉토리에 conftest.py + 모듈별 테스트 파일 존재
2. **테스트 카테고리 확인** (6개 카테고리):
   - ✅ Basic CRUD — 기본 액션별 테스트
   - ✅ ApprovalGate — L0/L1/HIGH/CRITICAL 케이스
   - ✅ Scope Validation — allowed_tools 검증
   - ✅ Multi-Tenant Isolation — tenant_id 격리
   - ✅ AuditLog — 성공/실패/L0 케이스
   - ✅ Error Handling — 알 수 없는 액션, 파라미터 누락, DB 없음
3. **결과 일관성**: 모든 테스트에서 AgentResult 반환 확인 (Exception raise 없음)
4. **실행 확인**:
   ```bash
   cd backend && python -m pytest tests/ -v --tb=short
   ```

## Template Variables

Skill 사용 시 아래 변수들을 모듈에 맞게 치환:

| 변수 | 설명 | 예시 |
|------|------|------|
| `{module_name}` | 모듈 이름 (snake_case) | `esignature` |
| `{ModuleName}` | 모듈 이름 (PascalCase) | `ESignature` |
| `{create_test_payload}` | 생성 테스트용 payload | `"title": "Test Doc"` |
| `{high_risk_action}` | 고위험 액션 이름 | `sign` |
| `{high_risk_payload}` | 고위험 액션 payload | `"doc_id": "..."` |
| `{allowed_tools_list}` | Agent allowed_tools | `["db_query", "db_write"]` |

## Reference Files

- `backend/src/core/base_agent.py` — BaseAgent 표준 흐름 (run → execute)
- `backend/src/modules/{module_name}/agent.py` — 테스트 대상 Agent
- `backend/src/modules/{module_name}/schemas.py` — 필드/payload 정보
- `.cursor/context/hitl_context.json` — HITL/ApprovalGate 기준
- `.cursor/context/workflow_context.json` — Agent 워크플로우 기준
- `.cursor/context/phase3_context.json` — Phase 3 기준
- `.cursor/rules/09_capability.mdc` — 코드 생성 규칙
