# 📘 AI Agent 문서용 MD → DOC 변환 & Obsidian 운영 가이드 (실무 템플릿 포함)

------------------------------------------------------------------------

title: "AI Agent 운영 문서 템플릿" author: "Dasom Guide" date:
"2026-02-23"

------------------------------------------------------------------------

# 🧭 문서 목적

이 문서는 Obsidian에서 작성한 Markdown(md)을 **Word(docx)** 로
변환하면서 아래 요소들을 자동으로 포함하도록 설계된 실무용 가이드입니다.

-   Cover Page (표지)
-   Title / Metadata
-   Table of Contents (목차)
-   Page Number (페이지 번호)
-   AI Agent 문서 표준 구조
-   Cursor Agent & Multi-Agent 문서 스타일

👉 그대로 복사해서 바로 사용 가능한 Template 입니다.

------------------------------------------------------------------------

# 🧱 1. AI Agent 표준 문서 구조 (Dasom Recommended)

## 📂 기본 문서 구조

    # Vision
    # Persona
    # Architecture
    # PRD
    # Integration Test
    # QA
    # Go Live

AI Agent 프로젝트에서는 구조가 매우 중요합니다.

특히:

-   Cursor → Architecture / Dev
-   Codex → Review / QA
-   Planner → Vision / Goal

처럼 역할을 분리하면 문서도 동일한 구조를 가져야 합니다.

------------------------------------------------------------------------

# 🎯 2. Cover Page 자동 생성 템플릿

Obsidian 문서 최상단에 아래 YAML을 넣으세요.

    ---
    title: "AI Agent MVP 운영 가이드"
    author: "Project Team"
    date: "2026"
    version: "v1.0"
    ---

DOC 변환 시 자동으로 문서 메타데이터로 들어갑니다.

------------------------------------------------------------------------

# 📑 3. 목차(Table of Contents) 자동 생성

Pandoc 옵션:

    --toc
    --number-sections

Heading 규칙:

    # Chapter 1
    ## Section 1.1
    ### Detail 1.1.1

Heading 구조가 깨지면 목차도 깨집니다.

------------------------------------------------------------------------

# 🔢 4. 페이지 번호 자동 적용

## 방법 1 (추천)

reference.docx 생성 후:

    삽입 → 페이지 번호 → 바닥글

이후 Pandoc 명령:

    pandoc input.md -o output.docx --reference-doc=reference.docx --toc

👉 디자인은 Word에서 관리하고 md는 구조만 유지합니다.

------------------------------------------------------------------------

# 🧩 5. Cursor Agent 문서 스타일 규칙

## ✔️ Rule

-   Heading level skip 금지
-   한 섹션 = 한 Agent 책임
-   PRD와 Architecture 반드시 분리

## ✔️ Example

    # Architecture (Cursor Owner)

    # QA (Codex Owner)

    # Persona (Planner Owner)

------------------------------------------------------------------------

# 🤖 6. Multi-Agent 문서 Template (실무용)

    # Vision

    ## Goal
    ## Problem
    ## Impact

    # Persona

    ## End User
    ## Operator
    ## Manager

    # Architecture

    ## Frontend
    ## Backend
    ## AI Layer

    # PRD

    ## Functional Requirement
    ## Non Functional Requirement

    # Integration Test

    # QA

    # Release Plan

------------------------------------------------------------------------

# 🎨 7. Obsidian에서 깔끔하게 보이게 하는 규칙

✔️ Heading 위아래 공백 1줄만\
✔️ 불필요한 HTML 태그 금지\
✔️ 리스트는 '-' 사용

좋은 md = 좋은 Word 문서

------------------------------------------------------------------------

# ⚙️ 8. 실무용 Pandoc 명령어 (복붙용)

    pandoc input.md -o output.docx ^
    --toc ^
    --number-sections ^
    --reference-doc=reference.docx

------------------------------------------------------------------------

# 📦 9. 바로 사용 가능한 AI Agent 문서 시작 템플릿

아래부터는 실제 프로젝트에서 바로 사용하는 시작 구조입니다.

------------------------------------------------------------------------

# Vision

프로젝트 비전 작성

------------------------------------------------------------------------

# Persona

-   End User
-   Operator
-   Manager

------------------------------------------------------------------------

# Architecture

Frontend / Backend / AI Agent 구조

------------------------------------------------------------------------

# PRD

요구사항 정의

------------------------------------------------------------------------

# Integration Test

통합 테스트 전략

------------------------------------------------------------------------

# QA

검수 기준

------------------------------------------------------------------------

# Go Live

릴리즈 계획

------------------------------------------------------------------------

# ✅ Dasom 실무 팁

-   Obsidian은 "구조", Word는 "디자인"
-   reference.docx 반드시 사용
-   Agent별 문서 책임 분리

이 템플릿은 AI Agent 기반 프로젝트에서 바로 사용 가능합니다.
