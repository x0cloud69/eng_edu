# 1.2 Persona Definition

**Project:** Standard Framework Project
**Phase:** 1. Vision & Role 정의
**산출물 ID:** 1.2 Persona_Spec.docx

| 항목 | 내용 |
|------|------|
| 문서 번호 | 1.2 Persona_Spec.docx |
| 버전 | v1.0 |
| 작성일 | 2026 |
| 작성자 | KY Song |
| 분류 | CONFIDENTIAL |
| 적용 대상 | Standard Framework 프로젝트 전체 |

---

## 목차

1. [개요](#1-개요)
2. [Persona 정의](#2-persona-정의)
   - 2.1 [Persona 1 — 공공기관 AI 아키텍트 (Primary)](#21-persona-1--공공기관-ai-아키텍트-primary)
   - 2.2 [Persona 2 — 개발 조직 테크리드 (Primary)](#22-persona-2--개발-조직-테크리드-primary)
   - 2.3 [Persona 3 — 보안 / 감사 담당자 (Secondary)](#23-persona-3--보안--감사-담당자-secondary)
   - 2.4 [Persona 4 — AI 운영 담당자 (Secondary)](#24-persona-4--ai-운영-담당자-secondary)
   - 2.5 [Persona 5 — 규제 기관 담당자 (Secondary)](#25-persona-5--규제-기관-담당자-secondary)
3. [Usage Scenario](#3-usage-scenario)
   - 3.1 [Scenario 1 — 신규 프로젝트 프레임워크 적용 (Happy Path)](#31-scenario-1--신규-프로젝트-프레임워크-적용-happy-path)
   - 3.2 [Scenario 2 — 감사 대응 요청 (Happy Path)](#32-scenario-2--감사-대응-요청-happy-path)
   - 3.3 [Scenario 3 — 비표준 요구사항 예외 처리 (Edge Case)](#33-scenario-3--비표준-요구사항-예외-처리-edge-case)
   - 3.4 [Scenario 4 — AI 오류 발생 대응 (Edge Case)](#34-scenario-4--ai-오류-발생-대응-edge-case)
4. [Context Requirements](#4-context-requirements)
5. [AI 개입 포인트 요약](#5-ai-개입-포인트-요약)
6. [승인 (Approval)](#6-승인-approval)

---

## 1. 개요

본 문서는 Standard Framework 프로젝트의 주요 사용자(Persona)를 정의하고, 각 Persona의 사용 시나리오(Usage Scenario)와 AI 시스템이 필요로 하는 컨텍스트 요구사항(Context Requirements)을 기술한다.

Problem Definition(1.1.1)의 'Who' 섹션에서 식별된 5개 이해관계자 그룹을 기반으로 Persona를 구체화하였으며, 각 Persona의 목표, Pain Point, 행동 패턴, AI 활용 방식을 정의한다.

> 💡 이 문서의 Persona 및 Scenario는 Phase 2 Workflow 설계, Phase 3 System Prompt 작성, Phase 4 Simulation 설계의 직접적인 입력값으로 활용된다.

---

## 2. Persona 정의

### 2.1 Persona 1 — 공공기관 AI 아키텍트 (Primary)

**기본 정보**

| 항목 | 내용 |
|------|------|
| 이름 (가명) | 김민준 (AI Architect, 중앙부처 디지털혁신팀) |
| 직군 / 역할 | 공공기관 AI 아키텍트 / 시스템 설계 책임자 |
| 경력 | IT 10년, AI 프로젝트 3년 |
| 기술 친숙도 | High — 클라우드, API, LLM 경험 보유 |
| 소속 조직 | Government / Agency |

**목표 & Pain Point**

| 항목 | 내용 |
|------|------|
| Goal | 부처 전체 AI 시스템에 일관된 표준 아키텍처 적용 |
| Pain Point | 프로젝트마다 아키텍처가 달라 유지보수 비용 증가 |
| | AI 의사결정 기록 체계 없어 감사 대응 시 수작업 |
| | 보안/컴플라이언스 기준을 매번 새로 정의해야 함 |
| Motivation | 한 번 만들어두면 모든 프로젝트에 재사용 가능한 표준 확보 |
| Frustration | 표준 없이 시작하면 나중에 리팩토링 비용이 더 크다 |

**AI 활용 방식**

| 항목 | 내용 |
|------|------|
| AI 사용 목적 | 아키텍처 표준 준수 여부 자동 검증, 산출물 초안 자동 생성 |
| 기대 행동 | 표준 위반 시 즉시 알림, 승인 없는 자동 실행 금지 |
| 신뢰 수준 | AI 추천은 참고하되 최종 결정은 본인이 한다 (L1 수준) |
| 우려 사항 | AI가 표준을 무시하고 임의로 구조를 변경하는 것 |

**성공 기준**

| 항목 | 내용 |
|------|------|
| 정량적 기준 | 신규 프로젝트 아키텍처 설계 시간 50% 단축 |
| 정성적 기준 | 표준 준수 여부를 AI가 자동 체크해줘서 안심하고 승인 가능 |
| KPI 연계 | 프레임워크 채택률 70% 이상 달성 시 성공 |

---

### 2.2 Persona 2 — 개발 조직 테크리드 (Primary)

**기본 정보**

| 항목 | 내용 |
|------|------|
| 이름 (가명) | 이서연 (Tech Lead, SI 개발사) |
| 직군 / 역할 | 개발 조직 테크리드 / 프로젝트 기술 책임 |
| 경력 | 개발 8년, 공공 프로젝트 4년 |
| 기술 친숙도 | High — Python, TypeScript, 클라우드 경험 |
| 소속 조직 | Development Organization |

**목표 & Pain Point**

| 항목 | 내용 |
|------|------|
| Goal | 공통 모듈 재사용으로 개발 기간 단축 및 품질 향상 |
| Pain Point | 프로젝트마다 권한관리, 로깅, API 구조를 처음부터 만들어야 함 |
| | 표준 없어서 팀원마다 코딩 스타일이 달라 코드 리뷰 부담 |
| | AI 거버넌스 요구사항이 프로젝트 중간에 추가되어 재작업 |
| Motivation | "이미 검증된 구조를 가져다 쓰면 비즈니스 로직에만 집중 가능" |
| Frustration | 문서화된 표준은 있는데 코드로 된 참조 구현이 없다 |

**AI 활용 방식**

| 항목 | 내용 |
|------|------|
| AI 사용 목적 | Framework 기반 코드 자동 생성, 코드 리뷰 보조 |
| 기대 행동 | Cursor에게 context 주면 표준에 맞는 코드를 바로 생성 |
| 신뢰 수준 | 코드 생성은 AI가 하되 최종 검수는 본인 (L1 수준) |
| 우려 사항 | AI가 생성한 코드가 보안 규칙이나 Audit Log를 빠뜨리는 것 |

**성공 기준**

| 항목 | 내용 |
|------|------|
| 정량적 기준 | 공통 모듈 재사용률 50% 이상, 개발 기간 30% 단축 |
| 정성적 기준 | 신규 개발자도 Framework만 보면 표준대로 개발 가능 |
| KPI 연계 | 중복 개발 비용 20~35% 절감 달성 시 성공 |

---

### 2.3 Persona 3 — 보안 / 감사 담당자 (Secondary)

**기본 정보**

| 항목 | 내용 |
|------|------|
| 이름 (가명) | 박지훈 (Compliance Officer, 감사팀) |
| 직군 / 역할 | 보안/감사 담당자 / AI 의사결정 추적 책임 |
| 경력 | 보안 감사 7년 |
| 기술 친숙도 | Medium — 로그 분석, 규정 검토 위주 |
| 소속 조직 | Security & Audit Department |

**목표 & Pain Point**

| 항목 | 내용 |
|------|------|
| Goal | AI 의사결정 100% 추적 가능, 감사 준비 기간 50% 단축 |
| Pain Point | AI가 어떤 근거로 추천했는지 설명할 수 없음 |
| | 감사 준비 시 로그 수집에 평균 4주 이상 소요 |
| | 시스템마다 로그 형식이 달라 통합 분석 불가 |
| Motivation | 표준화된 Audit Log로 감사 대응 시간을 획기적으로 단축 |
| Frustration | 로그가 있어도 형식이 달라서 분석할 수 없다 |

**성공 기준**

| 항목 | 내용 |
|------|------|
| 정량적 기준 | AI 의사결정 로그 100% 기록, 감사 준비 기간 50% 단축 |
| 정성적 기준 | 감사관이 로그만 보고도 AI 행동 경위 설명 가능 |
| KPI 연계 | 규제 준수율 95% 이상 달성 시 성공 |

---

### 2.4 Persona 4 — AI 운영 담당자 (Secondary)

**기본 정보**

| 항목 | 내용 |
|------|------|
| 이름 (가명) | 최수진 (AI Ops Manager, AI운영팀) |
| 직군 / 역할 | AI 운영 담당 / 모델 배포 및 모니터링 책임 |
| 경력 | AI 운영 4년 |
| 기술 친숙도 | High — MLOps, 모니터링 경험 |
| 소속 조직 | AI Operations Organization |

**목표 & Pain Point**

| 항목 | 내용 |
|------|------|
| Goal | 모델 승인·배포·모니터링 프로세스 표준화 및 30% 단축 |
| Pain Point | 모델 승인 절차가 팀마다 달라 평균 6~12주 소요 |
| | Drift 감지 체계가 없어 성능 저하를 사후에 발견 |
| | 책임 소재가 불명확해 장애 발생 시 원인 파악 지연 |
| Motivation | 표준화된 Release Gate와 자동 Drift 탐지로 운영 안정성 확보 |
| Frustration | 배포 후에 문제가 생겨도 어디서 잘못됐는지 추적이 안 된다 |

**성공 기준**

| 항목 | 내용 |
|------|------|
| 정량적 기준 | 모델 승인 30% 단축, Drift 자동 탐지 100% 적용 |
| 정성적 기준 | 배포 전 체크리스트만 따르면 누구나 안전하게 배포 가능 |
| KPI 연계 | Drift 자동 탐지 적용률 100% 달성 시 성공 |

---

### 2.5 Persona 5 — 규제 기관 담당자 (Secondary)

**기본 정보**

| 항목 | 내용 |
|------|------|
| 이름 (가명) | 정현우 (Policy Officer, 규제기관) |
| 직군 / 역할 | AI 규제 정책 담당 / 책임성·윤리 기준 준수 검토 |
| 경력 | 정책 분야 12년, AI 규제 3년 |
| 기술 친숙도 | Low~Medium — 정책 중심, 기술 세부사항 비전문 |
| 소속 조직 | Regulatory Agency |

**목표 & Pain Point**

| 항목 | 내용 |
|------|------|
| Goal | AI 책임성 및 윤리 기준 준수 95% 이상 보장 |
| Pain Point | AI 통제 체계가 불투명해 규제 준수 여부 확인 어려움 |
| | 기관마다 AI 시스템 구조가 달라 일관된 기준 적용 불가 |
| | 기술 용어 중심 문서로 정책 관점 검토가 어려움 |
| Motivation | 표준 프레임워크 채택 시 규제 준수 여부를 구조적으로 검증 가능 |
| Frustration | 잘 만들었다고 하는데 실제로 어떻게 통제되는지 설명을 못 한다 |

**성공 기준**

| 항목 | 내용 |
|------|------|
| 정량적 기준 | 규제 준수율 95% 이상, 리스크 보고 체계 표준화 |
| 정성적 기준 | 비기술 정책 담당자도 AI 통제 구조를 이해하고 검토 가능 |
| KPI 연계 | 감사 대응 시간 50% 단축 달성 시 성공 |

---

## 3. Usage Scenario

> 💡 각 Scenario는 Happy Path(정상 흐름)와 Edge Case(예외 상황)로 구분하며, Agent 개입 포인트를 명시한다.

### 3.1 Scenario 1 — 신규 프로젝트 프레임워크 적용 (Happy Path)

**Actor:** 김민준 (Persona 1) + 이서연 (Persona 2)
**목표:** 신규 AI 시스템 개발 착수 시 Framework 기반으로 표준 구조 셋업

| Step | Actor | 행동 | AI 개입 여부 |
|------|-------|------|-------------|
| 1 | 김민준 (AI Architect) | 신규 프로젝트 요구사항 정리 및 Authority Level 선정 | Agent 없음 (Human 작업) |
| 2 | Claude (AI) | Problem Definition 기반 project_context.json 자동 생성 | AI 자동 생성 (L1 승인 필요) |
| 3 | 김민준 | 생성된 JSON 검토 및 Governance Board 승인 요청 | Human 승인 게이트 |
| 4 | Governance Board | Authority Level 및 Risk 등급 공식 승인 | Human 최종 승인 |
| 5 | 이서연 (Tech Lead) | Cursor에 context 로드 후 Backend 뼈대 코드 생성 요청 | Cursor AI 실행 |
| 6 | Cursor (AI) | rules + context 기반 표준 준수 코드 자동 생성 | AI 자동 생성 (Audit Log 포함) |
| 7 | 이서연 | 생성 코드 검토 및 프로젝트 적용 | Human 검수 |

**예상 결과:** 신규 프로젝트 아키텍처 셋업 시간 기존 3~4주 → 3~5일로 단축

---

### 3.2 Scenario 2 — 감사 대응 요청 (Happy Path)

**Actor:** 박지훈 (Persona 3, 감사 담당자)
**목표:** 외부 감사 요청에 대해 AI 의사결정 이력 즉시 제공

| Step | Actor | 행동 | AI 개입 여부 |
|------|-------|------|-------------|
| 1 | 외부 감사관 | 특정 기간 AI 의사결정 로그 제출 요청 | Agent 없음 |
| 2 | 박지훈 | 감사 대응 Agent에 기간 및 범위 입력 | Human 요청 |
| 3 | Monitoring Agent | audit_logs 테이블 쿼리 및 집계 보고서 생성 | AI 자동 실행 (L1 승인) |
| 4 | 박지훈 | 보고서 검토 및 이상 항목 확인 | Human 검토 |
| 5 | Monitoring Agent | 이상 항목에 대한 상세 추적 경로 제공 | AI 자동 실행 |
| 6 | 박지훈 | 최종 보고서 승인 및 감사관 제출 | Human 최종 승인 |

**예상 결과:** 감사 준비 기간 기존 4주 이상 → 2~3일로 단축

---

### 3.3 Scenario 3 — 비표준 요구사항 예외 처리 (Edge Case)

**Actor:** 이서연 (Persona 2) — 특수 요구사항 발생
**상황:** 특정 기관 요구로 Framework 표준을 벗어난 구조가 필요한 경우

| Step | Actor | 행동 | AI 개입 여부 |
|------|-------|------|-------------|
| 1 | 이서연 | 표준 범위를 벗어난 커스텀 기능 요청 | Human 요청 |
| 2 | Orchestrator Agent | Scope 위반 감지 → 자동 실행 거부 + 에스컬레이션 | AI 자동 거부 (원칙 2) |
| 3 | 이서연 | 예외 승인 요청서 작성 (사유 + 영향 분석) | Human 작업 |
| 4 | Compliance Officer | Risk 재평가 수행 | Human 검토 |
| 5 | Governance Board | 예외 승인 또는 반려 결정 | Human 최종 결정 |
| 6 | 이서연 | 승인 시 — 예외 기록 후 제한적 구현 | Human 실행 + Audit Log |

> **핵심 포인트:** Agent는 Scope 초과를 자동 감지하고 거부한다. 예외는 반드시 Human 승인 후 진행.

---

### 3.4 Scenario 4 — AI 오류 발생 대응 (Edge Case)

**Actor:** 최수진 (Persona 4) — 운영 중 AI 오류 감지
**상황:** 운영 중 KPI Threshold 초과 또는 Drift 감지

| Step | Actor | 행동 | AI 개입 여부 |
|------|-------|------|-------------|
| 1 | Monitoring Agent | KPI 이상 또는 Drift 자동 감지 | AI 자동 탐지 |
| 2 | Monitoring Agent | 즉시 Incident 알림 발송 + 관련 로그 수집 | AI 자동 실행 (L1 승인) |
| 3 | 최수진 | Incident 내용 확인 및 영향 범위 파악 | Human 검토 |
| 4 | Orchestrator Agent | Risk CRITICAL → 해당 Agent 자동 실행 중단 | AI 자동 중단 (원칙 4) |
| 5 | AI Architect | Root Cause Analysis 수행 | Human 분석 |
| 6 | Evolution Agent | Context 수정 제안 생성 | AI 보조 (Governance 승인 필요) |
| 7 | Governance Board | 수정 승인 + Regression Test 후 재배포 | Human 최종 승인 |

> **핵심 포인트:** AI는 오류를 감지하면 즉시 중단하고 Human에게 에스컬레이션한다.

---

## 4. Context Requirements

각 Scenario에서 AI Agent가 올바르게 동작하기 위해 필요한 컨텍스트 요구사항을 정의한다.

| Context 항목 | 필요 | 설명 |
|-------------|------|------|
| Global Strategic Context | Y | project_context.json — Scope, Authority, KPI, Risk, Governance 포함. 모든 Agent 실행 전 로드 필수 |
| Governance Context | Y | governance.json — Authority Level, Risk 등급, 승인 체계. ApprovalGate 판단 기준 |
| Agent-Specific Context | Y | agents/{name}_context.json — 각 Agent의 허용 Scope, Tool, Skill 정의 |
| 사용자 역할/권한 정보 | Y | 요청자의 Role (Business Owner, Architect 등) — RBAC 적용 기준 |
| 세션 히스토리 | Y | 현재 세션의 이전 대화 및 실행 이력 — 연속성 있는 응답 위해 필요 |
| Audit Log 접근 권한 | Y | Scenario 2 감사 대응 시 audit_logs 테이블 조회 권한 필요 |
| KPI Baseline / Threshold | Y | Scenario 4 Drift 탐지 시 비교 기준값. operation_standards.json에 정의 |
| 실시간 모니터링 데이터 | Y | Scenario 4 — KPI 현재값, Drift 지표. Monitoring Agent가 실시간 수집 |
| 외부 규제 정보 | N | Phase 1 범위 외. 향후 Regulatory Agent 추가 시 필요 |
| 개인식별정보 (PII) | N | Restricted 등급 — 직접 처리 금지. 익명화 후 사용 |

---

## 5. AI 개입 포인트 요약

| Scenario | AI 개입 시점 | Agent | Authority Level | Human 개입 |
|---------|------------|-------|----------------|-----------|
| S1. 프레임워크 적용 | context.json 자동 생성 | Claude + Cursor | L1 | 승인 필수 |
| S1. 프레임워크 적용 | 표준 준수 코드 생성 | Cursor AI | L1 | 검수 필수 |
| S2. 감사 대응 | 로그 집계 보고서 생성 | Monitoring Agent | L1 | 검토 + 승인 |
| S3. 예외 처리 | Scope 위반 자동 거부 | Orchestrator Agent | L1 | 예외 승인 |
| S4. 오류 대응 | Drift / KPI 이상 탐지 | Monitoring Agent | L0 (자동) | 알림 수신 |
| S4. 오류 대응 | Agent 자동 실행 중단 | Orchestrator Agent | L1 | 원인 분석 |
| S4. 오류 대응 | Context 수정 제안 | Evolution Agent | L1 | Governance 승인 |

---

## 6. 승인 (Approval)

| 구분 | 내용 | 서명 | 날짜 |
|------|------|------|------|
| 작성자 | | | |
| 검토자 (AI Architect) | | | |
| 승인자 (Business Owner) | | | |
| 버전 | v1.0 | | |
