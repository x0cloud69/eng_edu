---
name: frontend-generator
description: >-
  Generates a complete frontend module (page + client component + endpoint constants + types)
  following the AI-Native SaaS Standard Framework pattern. Use when the user says
  "프론트 만들어줘", "페이지 생성", "화면 추가", "create frontend for XX module",
  "generate React page", or "XX 화면 추가해줘".
---

# Frontend Generator

You are a frontend module generator for the AI-Native SaaS Standard Framework.
When the user requests a frontend for a backend module, generate ALL files following the exact patterns below.

## Step 0: Gather Information

Ask the user (if not already provided):
1. **모듈 이름** (snake_case, 예: `esignature`, `payment`, `document`) — 백엔드 모듈과 동일
2. **엔티티 표시 필드** — 목록에서 보여줄 주요 필드 (예: title, amount, status)
3. **생성 폼 필드** — Create 폼에 필요한 입력 필드 (예: title: text, description: textarea, amount: number)
4. **Agent 연동 여부** — useAgent 훅으로 Orchestrator 경유할지, 직접 REST API 호출할지
5. **ApprovalGate 필요 여부** — 고위험 액션이 있는 모듈인지

## Step 1: Generate Files

모든 파일 위치 기준: `frontend/src/`

---

### 1-1. `api/endpoints.ts` — 엔드포인트 상수 추가

기존 `ENDPOINTS` 객체에 새 모듈 상수를 추가한다. **파일을 새로 만들지 말고 기존 파일에 추가**한다.

```typescript
// {MODULE_NAME} — 추가
{MODULE_UPPER}_LIST: "/api/v1/{module_name}",
{MODULE_UPPER}_DETAIL: (id: string) => `/api/v1/{module_name}/${id}`,
```

**규칙:**
- 기존 endpoints.ts에 병합 (파일 덮어쓰기 금지)
- 상수명: `{MODULE_UPPER}_LIST`, `{MODULE_UPPER}_DETAIL`
- prefix: `/api/v1/{module_name}`

---

### 1-2. `types/{module_name}.ts` — 엔티티 타입 정의

```typescript
/**
 * {ModuleName} 모듈 타입 정의
 */

export interface {EntityName} {
  id: string;
  tenant_id: string;
  {entity_fields}    // 예: title: string; amount: number; status: string;
  is_active: boolean;
  created_at: string;
}

export interface {EntityName}Create {
  {create_fields}    // 예: title: string; description?: string;
}

export interface {EntityName}Update {
  {update_fields}    // 예: title?: string; description?: string;
}

export interface {EntityName}PaginatedResponse {
  data: {
    items: {EntityName}[];
    total: number;
    page: number;
    size: number;
    total_pages: number;
  };
}

export interface {EntityName}ApiResponse {
  data: {EntityName};
}
```

**규칙:**
- 백엔드 schemas.py의 `Out`, `Create`, `Update`와 1:1 매핑
- PaginatedResponse, ApiResponse 래퍼 포함
- id, tenant_id, is_active, created_at 은 항상 포함

---

### 1-3. `app/{module_name}/page.tsx` — Next.js 페이지 (서버 컴포넌트)

```tsx
import { {ModuleName}Client } from "./{ModuleName}Client";

export default function {ModuleName}Page() {
  return (
    <div style={{ padding: 40, fontFamily: "sans-serif" }}>
      <h1>{모듈_한글명}</h1>
      <p>{모듈_설명}</p>
      <{ModuleName}Client />
    </div>
  );
}
```

**규칙:**
- 서버 컴포넌트 — `"use client"` 없음
- 실제 로직은 Client 컴포넌트에 위임
- 레이아웃은 기존 `app/layout.tsx` 상속

---

### 1-4. `app/{module_name}/{ModuleName}Client.tsx` — 클라이언트 컴포넌트 (핵심)

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { ENDPOINTS } from "../../api/endpoints";
import type {
  {EntityName},
  {EntityName}Create,
  {EntityName}PaginatedResponse,
  {EntityName}ApiResponse,
} from "../../types/{module_name}";

export function {ModuleName}Client() {
  const [items, setItems]       = useState<{EntityName}[]>([]);
  const [loading, setLoading]   = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError]       = useState<string | null>(null);

  // ── form state ──
  {form_state_declarations}
  // 예: const [title, setTitle] = useState("");
  //     const [description, setDescription] = useState("");

  // ── 목록 조회 ──
  const fetchItems = useCallback(() => {
    setLoading(true);
    apiClient
      .get<{EntityName}PaginatedResponse>(ENDPOINTS.{MODULE_UPPER}_LIST)
      .then((res) => setItems(res.data.items))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  // ── 생성 ──
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    {validation_check}    // 예: if (!title.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const body: {EntityName}Create = {
        {create_body}    // 예: title: title.trim(), description: description.trim() || undefined,
      };
      await apiClient.post<{EntityName}ApiResponse>(ENDPOINTS.{MODULE_UPPER}_LIST, body);
      {reset_form}       // 예: setTitle(""); setDescription("");
      fetchItems();
    } catch {
      setError("{한글_에러_메시지}");
    } finally {
      setSubmitting(false);
    }
  };

  // ── 삭제 ──
  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(ENDPOINTS.{MODULE_UPPER}_DETAIL(id));
      fetchItems();
    } catch {
      setError("삭제에 실패했습니다.");
    }
  };

  if (loading && items.length === 0) return <p>로딩 중...</p>;

  return (
    <div style={{ marginTop: 24 }}>
      {/* ── 생성 폼 ── */}
      <h2>{엔티티_한글명} 생성</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: 24 }}>
        {form_fields_jsx}
        {error && (
          <p style={{ color: "#c00", marginBottom: 8, fontSize: 14 }}>{error}</p>
        )}
        <button
          type="submit"
          disabled={submitting {disable_condition}}
          style={{
            padding: "8px 16px",
            background: "#028090",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            cursor: submitting ? "not-allowed" : "pointer",
            opacity: submitting ? 0.7 : 1,
          }}
        >
          {submitting ? "생성 중..." : "{엔티티_한글명} 생성"}
        </button>
      </form>

      {/* ── 목록 ── */}
      <h2>{엔티티_한글명} 목록</h2>
      {items.length === 0 ? (
        <p style={{ color: "#666" }}>등록된 {엔티티_한글명}이(가) 없습니다.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {items.map((item) => (
            <li
              key={item.id}
              style={{
                padding: 12,
                background: "#fff",
                border: "1px solid #eee",
                borderRadius: 6,
                marginBottom: 8,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                {display_fields_jsx}
              </div>
              <button
                onClick={() => handleDelete(item.id)}
                style={{
                  padding: "4px 12px",
                  background: "#eee",
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer",
                  fontSize: 12,
                }}
              >
                삭제
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**규칙:**
- `"use client"` 필수 (첫 줄)
- `apiClient` 사용 필수 (직접 fetch 금지)
- `ENDPOINTS` 상수 사용 필수 (URL 하드코딩 금지)
- types 파일에서 타입 import (inline 타입 선언 금지)
- 목록 조회: `PaginatedResponse` 래핑 → `res.data.items`
- 생성: `ApiResponse` 래핑
- 삭제: soft delete (DELETE → 204)
- 스타일: 기존 esignature 패턴 따름 (inline style, 브랜드 컬러 `#028090`)

---

### 1-5. (선택) Agent 연동 버전 — `useAgent` 훅 사용

Agent 연동이 필요한 경우, Client 컴포넌트에 추가:

```tsx
import { useAgent } from "../../hooks/useAgent";
import { ApprovalGate } from "../../components/ApprovalGate";

// 컴포넌트 내부에서:
const { run, approve, reject, loading: agentLoading, approval } = useAgent();

// Agent 호출 예시:
const handleAgentAction = async (action: string, payload: Record<string, unknown>) => {
  const result = await run({
    user_id: "current-user",
    action: `{module_name}.${action}`,
    payload,
    authority_level: "{authority_level}",
    risk_level: "{risk_level}",
  });

  if (result?.requires_approval) {
    // ApprovalGate가 자동으로 표시됨
  }
};

// JSX에 ApprovalGate 추가:
{approval?.required && !approval.approved && (
  <ApprovalGate
    level="{authority_level}"
    traceId={approval.trace_id}
    action="{module_name}.{action}"
    onApprove={(by) => approve(approval.trace_id, by)}
    onReject={reject}
    riskLevel="{risk_level}"
    hitlPattern="P1"
  />
)}
```

**규칙:**
- Agent 액션명: `{module_name}.{action}` 형식 (Orchestrator 라우팅)
- ApprovalGate: L1 이상 + 고위험 액션에서만 표시
- useAgent의 `run()` 은 반드시 Orchestrator 경유 (`/api/v1/agents/invoke`)

---

## Step 2: Sidebar 메뉴 등록

`frontend/src/components/Sidebar.tsx`에 새 메뉴 항목을 추가한다:

```tsx
// 기존 메뉴 배열에 추가
{ label: "{모듈_한글명}", href: "/{module_name}" },
```

---

## Step 3: Verify

생성 완료 후 다음을 확인한다:
1. `api/endpoints.ts` — 새 모듈 엔드포인트 추가 확인
2. `types/{module_name}.ts` — 백엔드 스키마와 1:1 매핑 확인
3. `app/{module_name}/page.tsx` — 서버 컴포넌트, Client 위임
4. `app/{module_name}/{ModuleName}Client.tsx` — "use client", apiClient, ENDPOINTS 사용
5. `components/Sidebar.tsx` — 메뉴 항목 추가
6. (선택) useAgent 훅 + ApprovalGate 연동

## Reference Files

- `frontend/src/app/esignature/` — 완전한 참조 구현
- `frontend/src/hooks/useAgent.ts` — Agent 훅 패턴
- `frontend/src/components/ApprovalGate.tsx` — 승인 게이트 UI
- `frontend/src/api/client.ts` — HTTP 클라이언트 표준
- `frontend/src/api/endpoints.ts` — 엔드포인트 상수
- `frontend/src/types/governance.ts` — 공통 타입 정의
- `.cursor/context/phase3_context.json` — Phase 3 기준
- `.cursor/rules/09_capability.mdc` — 코드 생성 규칙
