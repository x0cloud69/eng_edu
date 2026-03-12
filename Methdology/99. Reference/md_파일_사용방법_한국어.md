# MD 파일 사용 방법 (Markdown 가이드)

## 1. MD 파일이란?

MD 파일은 Markdown 문서입니다. 간단한 텍스트 기호를 사용하여 제목,
리스트, 체크박스 등의 구조를 만들 수 있는 파일입니다.

예시:

# 제목

## 부제목

-   리스트 항목 **굵은 글씨**

다음과 같은 도구에서 열 수 있습니다: - Obsidian - Cursor IDE - Visual
Studio Code

------------------------------------------------------------------------

## 2. 기본 Markdown 문법

### 제목 (Headings)

# H1 제목

## H2 섹션

### H3 하위섹션

### 리스트

-   항목 1
-   항목 2

번호 리스트: 1. 계획 2. 설계 3. 개발

### 체크박스

-   [ ] 해야 할 일
-   [x] 완료

### 코드 블록

    Agent: Planner
    Role: Architecture Design

### 링크 (Obsidian 스타일)

\[\[Persona Spec\]\] \[\[QA Checklist\]\]

------------------------------------------------------------------------

## 3. MD 파일 실제 사용 방법 (워크플로우)

Step 1 --- 파일 생성: AI-Agent-MVP.md

Step 2 --- 구조 작성: \# Vision \# Persona \# Architecture \# PR \#
Integration Test \# QA

Step 3 --- 프로젝트 진행하면서 계속 업데이트하는 Living Document로 사용

------------------------------------------------------------------------

## 4. AI Agent 시스템에서 MD 파일이 중요한 이유

MD 파일은 다음 역할을 할 수 있습니다:

-   프로젝트 문서 (Documentation)
-   시스템 Rule 정의
-   Agent Instructions
-   QA 체크리스트
-   Mission Control Spec

예시 폴더 구조:

/docs vision.md persona.md architecture.md qa.md

------------------------------------------------------------------------

## 5. 간단한 AI Agent 템플릿 예시

# Persona

Target: 독거노인 사용자 (Changsoon)

## Needs

-   안전
-   음성 기반 상호작용

# Agent Roles

-   Planner
-   Developer
-   QA

# Tasks

-   [ ] Architecture 정의
-   [ ] 기능 개발
-   [ ] 테스트 실행

