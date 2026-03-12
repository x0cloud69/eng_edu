# UI/UX Design Guide — AI-Native SaaS Framework

> Version: v1.0 | Date: 2026-03-11

---

## 1. 개요

### 목적
AI-Native SaaS 프레임워크의 표준 UI/UX 가이드라인을 정의하고, 일관된 사용자 경험과 기술 표준을 제공합니다.

### 기술 스택
- **Frontend**: Next.js 14+ (App Router)
- **UI Library**: shadcn/ui
- **Styling**: Tailwind CSS
- **Form Management**: react-hook-form + zod
- **State Management**: React Query
- **Date/Time**: date-fns

### 참조 문서
- `08_uiux.mdc` 규칙 참조
- `saas_foundation.json`
- `persona_context.json`
- `uiux_context.json`

---

## 2. 디자인 시스템

### 2.1 색상 토큰

#### 브랜드 색상
| 용도 | HEX | RGB | 용도 설명 |
|------|-----|-----|---------|
| Primary | #028090 | (2, 128, 144) | 메인 브랜드 색상, CTA 버튼 |
| Secondary | #1E2761 | (30, 39, 97) | 다크 테마, 헤더 배경 |

#### Risk Level 색상 (위험도)
| 레벨 | 색상 코드 | Tailwind | 의미 |
|------|---------|---------|------|
| LOW | #94D82D | `bg-green-400` | 낮음, 안전 |
| MEDIUM | #FFD43B | `bg-yellow-400` | 중간, 주의 필요 |
| HIGH | #FF922B | `bg-orange-400` | 높음, 위험 |
| CRITICAL | #FA5252 | `bg-red-500` | 긴급, 즉시 대응 |

#### Drift Level 색상
| 레벨 | 색상 코드 | Tailwind | 의미 |
|------|---------|---------|------|
| GREEN | #51CF66 | `text-green-600` | 정상 범위 |
| YELLOW | #FFD43B | `text-yellow-500` | 경고 범위 |
| RED | #FA5252 | `text-red-600` | 초과 범위 |

#### Status 색상 (상태)
| 상태 | 색상 코드 | Badge 스타일 |
|------|---------|-----------|
| ACTIVE | #228BE6 | `bg-blue-100 text-blue-800` |
| PENDING | #FFD43B | `bg-yellow-100 text-yellow-800` |
| APPROVED | #51CF66 | `bg-green-100 text-green-800` |
| REJECTED | #FA5252 | `bg-red-100 text-red-800` |
| DRAFT | #868E96 | `bg-gray-100 text-gray-800` |
| DEPLOYED | #228BE6 | `bg-blue-100 text-blue-800` |

#### 다크모드 지원
- 모든 컴포넌트에 `dark:` Tailwind 클래스 필수 적용
- 기본 배경: `bg-white dark:bg-slate-950`
- 기본 텍스트: `text-slate-900 dark:text-slate-50`
- 보더: `border-slate-200 dark:border-slate-800`

### 2.2 타이포그래피

#### 폰트 패밀리
```css
font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

#### 헤딩 스타일
| 레벨 | 크기 | 굵기 | Tailwind 클래스 | 용도 |
|------|------|------|----------------|------|
| H1 | 24px | 700 (bold) | `text-2xl font-bold` | 페이지 제목 |
| H2 | 20px | 700 (bold) | `text-xl font-bold` | 섹션 제목 |
| H3 | 16px | 600 (semibold) | `text-lg font-semibold` | 서브섹션 제목 |

#### 바디 텍스트
| 타입 | 크기 | 굵기 | Tailwind 클래스 | 용도 |
|------|------|------|----------------|------|
| Body | 14px | 400 (normal) | `text-sm` | 일반 본문 |
| Body Small | 12px | 400 (normal) | `text-xs` | 보조 텍스트 |
| Button | 14px | 500 (medium) | `text-sm font-medium` | 버튼 텍스트 |
| Label | 13px | 500 (medium) | `text-xs font-medium` | 입력 필드 라벨 |

#### 라인 높이
- Heading: 1.2
- Body: 1.5
- Compact: 1.3

### 2.3 간격 (Spacing)

Tailwind의 기본 4px 간격 시스템을 기반으로 합니다.

| 토큰 | 값 | Tailwind | 용도 |
|------|-----|---------|------|
| xs | 4px | `gap-1`, `p-1` | 아이콘 간격, 컴팩트 레이아웃 |
| sm | 8px | `gap-2`, `p-2` | 요소 간 기본 간격 |
| md | 16px | `gap-4`, `p-4` | 섹션 간 간격 |
| lg | 24px | `gap-6`, `p-6` | 컨테이너 패딩 |
| xl | 32px | `gap-8`, `p-8` | 주요 섹션 간격 |
| 2xl | 48px | `gap-12`, `p-12` | 페이지 메인 간격 |

#### 패딩 가이드
- 카드 컨테이너: `p-4` (16px)
- 폼 필드: `p-2` (8px)
- 대형 섹션: `p-6` (24px)
- 페이지 콘텐츠: `px-6 py-8` (24px / 32px)

---

## 3. 레이아웃 구조

### 3.1 Shell Layout

전체 애플리케이션의 기본 레이아웃 구조입니다.

```
┌─────────────────────────────────────────────────────┐
│                    Header (64px)                    │
├──────────────┬────────────────────────────────────┤
│              │                                    │
│  Sidebar     │      Content Area                  │
│  (256px or   │      (max-width: 1280px)          │
│  64px        │                                    │
│  collapsible) │      - Padding: 24px (lg)        │
│              │      - Responsive: full width    │
│              │        on mobile                  │
│              │                                    │
└──────────────┴────────────────────────────────────┘
```

#### 화면 너비별 조정
| Breakpoint | 조건 | 레이아웃 |
|-----------|------|--------|
| Mobile | < 768px | Sidebar 숨김 (Hamburger menu) |
| Tablet | 768px - 1024px | Collapsed sidebar (64px) |
| Desktop | ≥ 1024px | Full sidebar (256px) |

### 3.2 Navigation

#### 주요 네비게이션 8가지 경로

| 순번 | 라벨 | 경로 | 아이콘 | 설명 |
|------|------|------|--------|------|
| 1 | 대시보드 | `/` | 📊 Home | 메인 대시보드, KPI 시각화 |
| 2 | 전자서명 | `/esignature` | ✍️ FileText | 전자서명 관리 (기존 구현 완료) |
| 3 | 승인 관리 | `/approvals` | ✅ CheckCircle | Agent 액션 승인/거절 |
| 4 | 메뉴 관리 | `/menus` | 📋 Menu | 애플리케이션 메뉴 TreeView |
| 5 | 재사용 현황 | `/reuse` | 🔄 RotateCw | 모듈/프로젝트 재사용 통계 |
| 6 | KPI 모니터링 | `/monitoring` | 📈 TrendingUp | KPI 대시보드 및 Drift 분석 |
| 7 | Evolution | `/evolution` | 🚀 Rocket | Evolution proposal 및 패치노트 |
| 8 | 설정 | `/settings` | ⚙️ Settings | 시스템 설정, 사용자 관리 |

#### 네비게이션 구현 규칙
- 모든 라우트는 `<Link>` 컴포넌트 사용
- 활성 경로는 `aria-current="page"` 속성 필수
- 아이콘 + 라벨 함께 표시 (모바일에서는 토글 가능)
- Keyboard 네비게이션 지원: Tab, Arrow keys

---

## 4. 공통 컴포넌트

### 4.1 UI Components (shadcn/ui 기반)

| 컴포넌트 | 용도 | 상태 | 위치 |
|---------|------|------|------|
| StatusBadge | 상태 표시 (ACTIVE, PENDING, etc.) | 구현 완료 | `components/ui/status-badge.tsx` |
| DataTable | 데이터 목록 표시, 정렬, 필터링 | 구현 완료 | `components/ui/data-table.tsx` |
| EmptyState | 데이터 없음 상태 화면 | 구현 완료 | `components/ui/empty-state.tsx` |
| PageHeader | 페이지 제목, 설명, CTA 버튼 | 구현 완료 | `components/ui/page-header.tsx` |
| KPICard | KPI 수치 표시 (K-01~K-07) | 구현 완료 | `components/ui/kpi-card.tsx` |
| SkeletonTable | 로딩 상태 (DataTable 스켈레톤) | 구현 완료 | `components/ui/skeleton-table.tsx` |
| Card | 기본 카드 컨테이너 | shadcn/ui | - |
| Button | 버튼 (Primary, Secondary, Destructive) | shadcn/ui | - |
| Dialog/Modal | 모달 다이얼로그 | shadcn/ui | - |
| Tabs | 탭 네비게이션 | shadcn/ui | - |
| Input | 텍스트 입력 필드 | shadcn/ui | - |
| Select | 드롭다운 선택 | shadcn/ui | - |
| Checkbox | 체크박스 | shadcn/ui | - |
| Radio | 라디오 버튼 | shadcn/ui | - |
| Textarea | 긴 텍스트 입력 | shadcn/ui | - |
| Alert | 알림 메시지 | shadcn/ui | - |
| Tooltip | 호버 텍스트 | shadcn/ui | - |
| Pagination | 페이지 네비게이션 | shadcn/ui | - |
| Dropdown Menu | 드롭다운 메뉴 | shadcn/ui | - |

### 4.2 Agent Components (커스텀)

| 컴포넌트 | 용도 | 상태 | 위치 |
|---------|------|------|------|
| ApprovalGate | HIGH+ 비가역 액션 승인 모달 | 구현 완료 | `components/agent/approval-gate.tsx` |
| AgentStatusBadge | Agent 실행 상태 배지 (RUNNING, COMPLETED, FAILED) | 구현 완료 | `components/agent/agent-status-badge.tsx` |
| ExecutionTimeline | Agent 실행 시간축 로그 | 구현 완료 | `components/agent/execution-timeline.tsx` |
| RiskBanner | 위험도 경고 배너 (HIGH, CRITICAL) | 구현 완료 | `components/agent/risk-banner.tsx` |
| AuditLogTable | Audit 로그 테이블 | 구현 완료 | `components/agent/audit-log-table.tsx` |

### 4.3 컴포넌트 사용 우선순위

**중요**: 다음 우선순위를 따릅니다.

1. **1순위**: `shadcn/ui` 공식 컴포넌트
   - Button, Card, Dialog, Input, Select, Tabs 등
   - 이미 설치되어 있음

2. **2순위**: `components/ui/` 커스텀 컴포넌트
   - 프로젝트 고유 컴포넌트
   - StatusBadge, DataTable, EmptyState 등

3. **3순위**: `components/agent/` Agent 전용 컴포넌트
   - ApprovalGate, AgentStatusBadge 등

4. **신규 생성**: 위 3가지로 충족 불가능할 경우만
   - 설계 검토 필수
   - `components/ui/` 또는 `components/agent/` 하위 생성

---

## 5. 페이지 설계

### 5.1 대시보드 (/)

**목적**: 시스템 전체 현황 조회, KPI 모니터링, 최근 활동 확인

#### 레이아웃
```
┌─────────────────────────────────────┐
│ Page Header: "Dashboard"            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ KPI Cards (7개, 그리드 레이아웃)     │
│ K-01 | K-02 | K-03 | K-04          │
│ K-05 | K-06 | K-07                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Agent Status Overview               │
│ - Active Agents (카드)              │
│ - Agent Health (색상 인디케이터)    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Recent Activities (최근 활동 목록)   │
│ - DataTable (5개 항목 미리보기)      │
│ - "View All" 링크 → /approvals     │
└─────────────────────────────────────┘
```

#### KPI 카드 구성
- **KPI-01~07**: 각 카드에 수치, 전월 대비 증감률, 트렌드 미니차트 포함
- **컬러**: Primary 색상 + 위험도 인디케이터 (HIGH는 오렌지, CRITICAL은 빨강)
- **반응형**: 모바일 1열, 태블릿 2열, 데스크톱 3~4열

#### 구현 컴포넌트
- `<KPICard />` × 7
- `<Card />` × 2 (Agent Status, Recent Activities)
- `<DataTable />` (Recent Activities)
- `<AgentStatusBadge />`
- `<RiskBanner />` (높은 위험 아이템 있을 시)

---

### 5.2 전자서명 (/esignature)

**상태**: 기존 구현 완료

**참조**: 기존 `/esignature` 페이지 구현 참조

---

### 5.3 승인 관리 (/approvals)

**목적**: Agent 액션 승인/거절, 승인 이력 관리

#### 레이아웃
```
┌─────────────────────────────────────┐
│ Page Header: "Approval Management"  │
│ 설명: "HIGH 레벨 이상 액션 승인"    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Tabs: Pending | History             │
│                                     │
│ [Pending Tab]                       │
│ - DataTable (승인 대기 항목들)      │
│   - Risk Level (색상)               │
│   - Agent Name                      │
│   - Action Description              │
│   - Created At                      │
│   - Actions (Approve/Reject 버튼)  │
│ - EmptyState (대기 항목 없을 시)   │
│                                     │
│ [History Tab]                       │
│ - DataTable (승인 이력)             │
│   - Status (APPROVED/REJECTED)      │
│   - Approved/Rejected By            │
│   - Timestamp                       │
└─────────────────────────────────────┘
```

#### ApprovalGate 모달
- Approve 또는 Reject 버튼 클릭 시 모달 표시
- 액션 상세 정보 표시
- 승인 사유 입력 (optional textarea)
- 최종 확인 버튼 (Approve/Reject)

#### 구현 컴포넌트
- `<Tabs />` (Pending/History)
- `<DataTable />`
- `<EmptyState />`
- `<ApprovalGate />` (모달)
- `<StatusBadge />` (Status 표시)
- `<RiskBanner />`

---

### 5.4 메뉴 관리 (/menus)

**목적**: 애플리케이션 메뉴 계층 관리 (TreeView)

#### 레이아웃
```
┌─────────────────────────────────────┐
│ Page Header: "Menu Management"      │
│ CTA: "+ Add Menu" 버튼              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ TreeView (계층 메뉴 표시)            │
│ ├─ Menu 1                           │
│ │  ├─ Submenu 1-1                  │
│ │  └─ Submenu 1-2                  │
│ ├─ Menu 2                           │
│ └─ Menu 3                           │
│    └─ Submenu 3-1                  │
│       └─ Sub-submenu 3-1-1         │
│                                     │
│ [우클릭 컨텍스트 메뉴]              │
│ - Edit                              │
│ - Delete                            │
│ - Add Child                         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 우측 패널 (선택된 메뉴 상세)         │
│ - Menu Name                         │
│ - URL Path                          │
│ - Icon                              │
│ - Permission Level                  │
│ - Active/Inactive Toggle            │
│ - Save/Cancel 버튼                  │
└─────────────────────────────────────┘
```

#### 구현 기술
- shadcn/ui의 Tree 컴포넌트 또는 커스텀 TreeView
- 드래그 드롭 (재정렬)
- 인라인 편집 모드

---

### 5.5 재사용 현황 (/reuse)

**목적**: 모듈/프로젝트 재사용 통계 조회

#### 레이아웃
```
┌─────────────────────────────────────┐
│ Page Header: "Reuse Overview"       │
└─────────────────────────────────────┘

┌──────────┬──────────────────────────┐
│ KPI-01   │ KPI-02                  │
│ (재사용  │ (프로젝트 재사용율)      │
│ 모듈수)  │                         │
└──────────┴──────────────────────────┘

┌─────────────────────────────────────┐
│ Modules DataTable                   │
│ - Module Name                       │
│ - Reuse Count                       │
│ - Last Used Date                    │
│ - Status (ACTIVE/DEPRECATED)       │
│ - Action: View Details              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Projects DataTable                  │
│ - Project Name                      │
│ - Reused Modules Count              │
│ - Reuse Ratio (%)                   │
│ - Last Updated                      │
│ - Action: View Details              │
└─────────────────────────────────────┘
```

#### 구현 컴포넌트
- `<KPICard />` × 2 (K-01, K-02)
- `<DataTable />` × 2 (Modules, Projects)
- `<Tabs />` (선택 사항: 모듈/프로젝트 탭 분리)

---

### 5.6 KPI 모니터링 (/monitoring)

**목적**: KPI 대시보드, Drift 분석, Alert 목록 조회

#### 레이아웃
```
┌─────────────────────────────────────┐
│ Page Header: "KPI Monitoring"       │
│ 필터: Date Range (date-fns 사용)   │
└─────────────────────────────────────┘

┌──────────┬──────────┬──────────┐
│ KPI-01   │ KPI-02   │ KPI-03  │
└──────────┴──────────┴──────────┘
┌──────────┬──────────┬──────────┐
│ KPI-04   │ KPI-05   │ KPI-06  │
└──────────┴──────────┴──────────┘
┌──────────────────────────────────────┐
│ KPI-07   (전체 너비)                  │
└──────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Drift Analysis (차트)                │
│ - Line Chart (KPI별 Drift 추이)    │
│ - 범위: GREEN/YELLOW/RED           │
│ - 범례, 호버 툴팁                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Alerts & Anomalies                  │
│ - DataTable (Alert 목록)            │
│   - Alert Level (MEDIUM/HIGH/...)  │
│   - KPI Name                        │
│   - Drift Amount                    │
│   - Timestamp                       │
│   - Status (OPEN/CLOSED)            │
│ - 필터: Level, KPI, Status         │
└─────────────────────────────────────┘
```

#### Drift 차트 색상 규칙
- **GREEN Zone**: 정상 범위 (초록색 배경)
- **YELLOW Zone**: 경고 범위 (노란색 배경)
- **RED Zone**: 초과 범위 (빨강색 배경)
- **선 색상**: KPI별로 다른 색상 적용

#### 구현 컴포넌트
- `<KPICard />` × 7
- Chart library (recharts 또는 chart.js)
- `<DataTable />` (Alerts)
- `<FilterBar />` (Date range, Level, Status)
- `<RiskBanner />` (높은 위험 알림)

---

### 5.7 Evolution 관리 (/evolution)

**목적**: Evolution proposal 관리, Drift 분석 결과 조회, 패치 노트

#### 레이아웃
```
┌─────────────────────────────────────┐
│ Page Header: "Evolution Management" │
│ CTA: "+ Create Proposal" 버튼       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Tabs: Proposals | Drift Analysis | Patch Notes
│                                     │
│ [Proposals Tab]                     │
│ - DataTable (Proposal 목록)         │
│   - Title                           │
│   - Status (DRAFT/PENDING/APPROVED) │
│   - Created Date                    │
│   - Action: View Details/Edit/Delete│
│ - EmptyState                        │
│                                     │
│ [Drift Analysis Tab]                │
│ - 분석 결과 목록                     │
│ - 상세 차트 및 통계                  │
│                                     │
│ [Patch Notes Tab]                   │
│ - 버전별 패치 노트 (최신순)        │
│ - Markdown 렌더링                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ [상세 페이지 (Proposal 클릭 시)]    │
│ - Proposal Header (제목, 상태)      │
│ - 상세 정보 (Tabs)                  │
│   - Overview (설명, 메타데이터)    │
│   - Drift Impact (영향 분석)       │
│   - Implementation (구현 계획)      │
│   - Review (리뷰 코멘트)           │
│ - ApprovalGate 모달 (승인 필요 시) │
└─────────────────────────────────────┘
```

#### 구현 컴포넌트
- `<Tabs />`
- `<DataTable />`
- `<EmptyState />`
- `<StatusBadge />`
- `<PageHeader />`
- `<ApprovalGate />` (승인 필요 시)
- Chart library (Drift 분석 차트)

---

## 6. 화면 유형별 패턴

### 패턴 정의 및 사용 가이드

| 패턴 | 구성 요소 | 레이아웃 | 사용 예시 | 필수 컴포넌트 |
|------|---------|--------|---------|------------|
| **목록** (List) | FilterBar + DataTable + Pagination + EmptyState | 전체 너비 테이블 | /approvals, /reuse | `<DataTable />`, `<EmptyState />`, `<Pagination />` |
| **상세** (Detail) | PageHeader + Tabs + 폼/데이터 표시 | 좌측 네비게이션 + 우측 콘텐츠 | 아이템 상세 페이지 | `<PageHeader />`, `<Tabs />`, `<Card />` |
| **폼** (Form) | FormField (react-hook-form + zod) + ApprovalGate + 이탈 경고 | 중앙 집중식, max-width 600px | 생성/편집 페이지 | `<Input />`, `<ApprovalGate />`, `<Alert />` |
| **대시보드** (Dashboard) | KPICard + Charts + RiskBanner + 샘플 데이터 | 그리드 레이아웃 + 풀 너비 차트 | /, /monitoring | `<KPICard />`, `<Card />`, Chart library |

#### 목록 패턴 상세
```tsx
// 구조
<PageHeader title="항목 목록" />
<FilterBar
  filters={[
    { label: "Status", type: "select", options: [...] },
    { label: "Date Range", type: "dateRange" },
  ]}
  onFilterChange={handleFilter}
/>
<DataTable
  columns={[...]}
  data={items}
  pagination={{ page, pageSize, total }}
/>
{items.length === 0 && <EmptyState />}
```

#### 상세 패턴 상세
```tsx
// 구조
<PageHeader
  title={item.name}
  description={item.description}
  action={<Button>Edit</Button>}
/>
<Tabs defaultValue="overview">
  <TabsContent value="overview">
    {/* 기본 정보 */}
  </TabsContent>
  <TabsContent value="details">
    {/* 상세 정보 */}
  </TabsContent>
</Tabs>
```

#### 폼 패턴 상세
```tsx
// 구조
<Card className="max-w-2xl mx-auto">
  <CardHeader>
    <CardTitle>폼 제목</CardTitle>
  </CardHeader>
  <CardContent>
    <FormField
      control={form.control}
      name="fieldName"
      render={({ field }) => (
        <FormItem>
          <FormLabel>필드명</FormLabel>
          <FormControl>
            <Input {...field} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  </CardContent>
  <CardFooter>
    <Button onClick={handleSubmit}>저장</Button>
    {showWarning && <Alert>나가면 작성 내용이 사라집니다</Alert>}
  </CardFooter>
</Card>

// HIGH+ 액션 시:
<ApprovalGate
  action={action}
  onApprove={submitForm}
/>
```

---

## 7. Agent 전용 UI 규칙

### 7.1 비가역 액션 (Irreversible Actions)

**규칙**: Risk Level이 `HIGH` 이상인 모든 비가역 액션에는 `<ApprovalGate />` 모달 필수

#### 비가역 액션 예시
- 데이터 삭제
- 시스템 설정 변경
- Evolution 배포
- 메뉴 구조 변경 (전파 영향)
- Agent 정책 변경

#### ApprovalGate 사용법
```tsx
const handleHighRiskAction = () => {
  setShowApprovalGate(true);
};

const handleApprove = async (approvalData) => {
  // 실제 액션 실행
  await executeAction(approvalData);
  setShowApprovalGate(false);
};

return (
  <>
    <Button onClick={handleHighRiskAction} variant="destructive">
      Delete
    </Button>
    <ApprovalGate
      isOpen={showApprovalGate}
      action={{
        title: "Delete Item",
        description: "이 항목을 삭제합니다",
        riskLevel: "HIGH",
      }}
      onApprove={handleApprove}
      onCancel={() => setShowApprovalGate(false)}
    />
  </>
);
```

### 7.2 Agent 실행 화면

**규칙**: Agent가 실행 중일 때 다음 UI 요소 필수 표시

#### 필수 UI 요소
1. **AgentStatusBadge**: 현재 상태 표시 (RUNNING, COMPLETED, FAILED, CANCELLED)
2. **ExecutionTimeline**: 실행 단계별 로그 표시
3. **Realtime Feedback**: 실행 중 메시지 업데이트 (WebSocket/SSE)

#### 예시 구현
```tsx
const [execution, setExecution] = useState(null);

useEffect(() => {
  // Agent 실행 구독
  const unsubscribe = subscribeToExecution(agentId, (update) => {
    setExecution(update);
  });
  return unsubscribe;
}, [agentId]);

return (
  <div>
    <AgentStatusBadge
      status={execution?.status}
      icon={execution?.icon}
    />
    <ExecutionTimeline
      logs={execution?.logs}
      status={execution?.status}
    />
    {execution?.status === 'FAILED' && (
      <RiskBanner
        level="CRITICAL"
        message={execution?.error}
      />
    )}
  </div>
);
```

### 7.3 useAgent() Hook 사용 필수

**규칙**: Agent 기능 호출 시 반드시 `useAgent()` 훅 경유

#### 금지 사항
- ❌ 직접 fetch(`/api/agent/...`) 호출
- ❌ 직접 axios.post로 API 호출

#### 올바른 방식
```tsx
import { useAgent } from '@/hooks/use-agent';

export function MyComponent() {
  const { executeAction, status, error, logs } = useAgent();

  const handleClick = async () => {
    await executeAction('actionName', { param: value });
  };

  return (
    <div>
      <AgentStatusBadge status={status} />
      <ExecutionTimeline logs={logs} />
      {error && <RiskBanner level="CRITICAL" message={error} />}
    </div>
  );
}
```

### 7.4 Risk Level에 따른 UI 처리

| Risk Level | ApprovalGate | RiskBanner | 색상 |
|-----------|-------------|-----------|------|
| LOW | - | - | 회색 |
| MEDIUM | - | ⚠️ 경고 (선택) | 노랑 |
| HIGH | ✓ 필수 | ⚠️ 필수 | 주황 |
| CRITICAL | ✓ 필수 | ⚠️ 필수 | 빨강 |

---

## 8. 접근성 (Accessibility, WCAG 2.1 AA)

### 8.1 기본 규칙

모든 UI 컴포넌트는 WCAG 2.1 AA 표준을 만족해야 합니다.

### 8.2 필수 구현 사항

#### 1. ARIA 속성
```tsx
// 라벨 연결
<label htmlFor="email">이메일</label>
<input id="email" type="email" />

// ARIA Label (라벨이 없는 경우)
<button aria-label="메뉴 닫기" onClick={closeMenu}>
  <X size={24} />
</button>

// ARIA Current (활성 페이지)
<a href="/dashboard" aria-current="page">대시보드</a>
```

#### 2. 포커스 관리
```tsx
// Focus Visible (outline)
<button className="focus:outline-2 focus:outline-offset-2 focus:outline-blue-500">
  Click me
</button>

// Focus 순서
// Tab 키로 논리적 순서 이동 (z-index 영향 없음)
```

#### 3. 최소 터치 타겟 크기
```tsx
// 최소 44×44px (웹 표준)
<button className="min-h-11 min-w-11">
  {/* 44px × 44px 이상 */}
</button>
```

#### 4. 색상 대비
| 텍스트 크기 | 최소 명도 대비 |
|----------|------------|
| 일반 (14px) | 4.5:1 |
| 큰 (18px+) | 3:1 |
| UI 요소 | 3:1 |

#### 5. 폼 필드
```tsx
// 1. 라벨 필수
<FormItem>
  <FormLabel htmlFor="name">이름</FormLabel>
  <FormControl>
    <Input id="name" />
  </FormControl>
  <FormDescription>필수 항목</FormDescription>
  <FormMessage /> {/* 에러 메시지 */}
</FormItem>

// 2. 에러 메시지 aria-describedby로 연결
<Input
  aria-describedby="error-email"
  aria-invalid={hasError}
/>
<span id="error-email" role="alert">
  유효한 이메일을 입력하세요
</span>
```

#### 6. 이미지 및 아이콘
```tsx
// 1. Alt 텍스트 (이미지)
<img src="/logo.png" alt="회사 로고" />

// 2. 아이콘 (표현 목적)
<button aria-label="삭제">
  <Trash2 size={20} aria-hidden="true" />
</button>

// 3. 배경 이미지 (화장용)
<div
  className="bg-cover"
  style={{ backgroundImage: 'url(...)' }}
  role="presentation"
/>
```

#### 7. 키보드 네비게이션
```tsx
// 1. Tab 네비게이션
// - tabindex는 최대 필요시만 사용 (보통 -1)
<button tabIndex={-1}>숨김 버튼</button>

// 2. Enter/Space 키
<button onClick={handleClick}>버튼</button>

// 3. Escape 키 (모달 닫기)
<Dialog open={open} onOpenChange={setOpen}>
  {/* Escape로 자동 닫힘 */}
</Dialog>

// 4. Arrow 키 (Tabs, SelectBox 등)
<Tabs> {/* 자동 지원 */} </Tabs>
```

#### 8. 스크린 리더 지원
```tsx
// Skip Links
<a href="#main-content" className="sr-only">
  메인 콘텐츠로 건너뛰기
</a>

// Live Regions
<div role="status" aria-live="polite" aria-atomic="true">
  저장되었습니다
</div>

// Loading State
<div role="status" aria-live="polite">
  <span className="sr-only">로딩 중...</span>
  <LoadingSpinner />
</div>
```

### 8.3 검증 방법
- 🔍 axe DevTools (Chrome 확장)
- 🔍 WAVE (webaim.org/wave)
- 🔍 스크린 리더 테스트 (NVDA, JAWS)
- ⌨️ 키보드만으로 네비게이션

---

## 9. 산출물 목록

### 9.1 문서 및 설정 파일

| 파일명 | 용도 | 상태 |
|--------|------|------|
| `uiux_context.json` | UI/UX 컨텍스트 (색상, 폰트, 컴포넌트) | 참조 |
| `ui_ux_design_guide.md` | 이 문서 (UI/UX 설계 가이드) | 작성 중 |
| `saas_foundation.json` | SaaS 기본 설정 (기술 스택 등) | 참조 |
| `persona_context.json` | 사용자 페르소나 정의 | 참조 |

### 9.2 UI 컴포넌트 (6개 기본)

| 컴포넌트 | 파일 경로 | 상태 |
|---------|---------|------|
| StatusBadge | `components/ui/status-badge.tsx` | ✅ |
| DataTable | `components/ui/data-table.tsx` | ✅ |
| EmptyState | `components/ui/empty-state.tsx` | ✅ |
| PageHeader | `components/ui/page-header.tsx` | ✅ |
| KPICard | `components/ui/kpi-card.tsx` | ✅ |
| SkeletonTable | `components/ui/skeleton-table.tsx` | ✅ |

### 9.3 Agent 컴포넌트 (5개 전용)

| 컴포넌트 | 파일 경로 | 상태 |
|---------|---------|------|
| ApprovalGate | `components/agent/approval-gate.tsx` | ✅ |
| AgentStatusBadge | `components/agent/agent-status-badge.tsx` | ✅ |
| ExecutionTimeline | `components/agent/execution-timeline.tsx` | ✅ |
| RiskBanner | `components/agent/risk-banner.tsx` | ✅ |
| AuditLogTable | `components/agent/audit-log-table.tsx` | ✅ |

### 9.4 페이지 및 모듈 (6개 주요)

| 페이지 | 경로 | 상태 | 컴포넌트 |
|--------|------|------|---------|
| 대시보드 | `/` | ✅ | KPICard, AgentStatusBadge, DataTable |
| 전자서명 | `/esignature` | ✅ | 기존 구현 참조 |
| 승인 관리 | `/approvals` | 🟡 | DataTable, ApprovalGate, Tabs |
| 메뉴 관리 | `/menus` | 🟡 | TreeView, Card, Button |
| 재사용 현황 | `/reuse` | 🟡 | KPICard, DataTable |
| KPI 모니터링 | `/monitoring` | 🟡 | KPICard, Chart, DataTable, RiskBanner |
| Evolution | `/evolution` | 🟡 | DataTable, Tabs, ApprovalGate |

**범례**: ✅ 완료, 🟡 진행 중, ⏳ 대기

### 9.5 기타 산출물

| 항목 | 설명 | 상태 |
|------|------|------|
| Word Document | UI/UX 설계 가이드 (Word 형식) | 🟡 |
| Design System Figma | 디자인 시스템 (선택) | ⏳ |
| Component Storybook | 컴포넌트 카탈로그 | ⏳ |

---

## 10. 참조 문서

### 공식 문서
- [shadcn/ui 공식 사이트](https://ui.shadcn.com)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [Next.js 14 문서](https://nextjs.org/docs)
- [react-hook-form 문서](https://react-hook-form.com)
- [React Query 문서](https://tanstack.com/query/latest)
- [WCAG 2.1 가이드](https://www.w3.org/WAI/WCAG21/quickref/)

### 프로젝트 문서
- `08_uiux.mdc` - UI/UX 마크다운 규칙
- `saas_foundation.json` - SaaS 기반 설정
- `persona_context.json` - 사용자 페르소나
- `uiux_context.json` - 색상, 폰트, 컴포넌트 정의

### 참고 자료
- [디자인 토큰 가이드](https://www.designtokens.org/)
- [모바일 우선 설계](https://www.smashingmagazine.com/2013/05/mobile-first-css-sass-layering/)
- [접근성 체크리스트](https://www.a11yproject.com/checklist/)

---

## 11. 변경 이력

| 버전 | 날짜 | 변경 사항 |
|------|------|---------|
| v1.0 | 2026-03-11 | 초안 작성 (섹션 1-10 완성) |

---

**작성자**: AI-Native SaaS Framework Team
**최종 검토**: 2026-03-11
**다음 검토 예정**: 2026-04-11
