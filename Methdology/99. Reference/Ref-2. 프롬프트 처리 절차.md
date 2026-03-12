# Cursor에서 "프로젝트 초안 만들어줘" 처리 절차

Context, Rule, Skill 정보만 있는 상태에서 초기 프로젝트 생성 시, 사용자가 **"프로젝트 초안 만들어줘"**라고 했을 때 Cursor 내부에서 이루어지는 절차를 정리한 문서입니다.

---

## 1. 요청 수신 및 컨텍스트 구성

- **사용자 메시지**: "프로젝트 초안 만들어줘"
- **시스템에 이미 포함되는 것**:
  - **Rules**: `CLAUDE.md` 등 (프로젝트 규칙, 기술 스택, 레이아웃 등)
  - **Context**: `.cursor/context/*.json` 중 로드되는 것들
  - **Skills 목록**: 각 스킬의 `name`, `fullPath`, `description`만 (스킬 **내용**은 아직 안 읽음)

이 시점에는 **context, rule, skill 메타정보만 있는 상태**입니다.

---

## 2. 스킬 선택 (의미 매칭)

- 에이전트(LLM)가 **Skills 목록의 description**만 보고 판단합니다.
- "프로젝트 초안" ≈ "새 프로젝트 설정 / 프로젝트 초기화 / context 생성"으로 해석되면  
  → **context-generator** 스킬을 사용하기로 결정합니다.
- **예약어가 아니라**, description 문장과 사용자 문장의 **의미 유사도**로 선택합니다.

---

## 3. 스킬 파일 읽기

- 선택된 스킬의 **내용**은 아직 없으므로:
  - **Read** 도구로 `.cursor/skills/context-generator/SKILL.md` 를 읽습니다.
- 읽은 뒤에야 Step 0, Step 1, Step 2 … 같은 **절차**를 알 수 있습니다.

---

## 4. Step 0 실행 (정보 수집)

- SKILL.md에 "대화형으로 수집하라"고 되어 있으면:
  - 프로젝트 이름, 핵심 문제, 이해관계자, KPI, 기술 스택, 페르소나, In/Out-Scope 등을
  - **추가 질문**으로 한 번에 묻거나, 짧게 나눠서 묻습니다.
- 사용자가 답하면 그 내용을 바탕으로 다음 단계에서 JSON을 채웁니다.

---

## 5. Step 1 ~ Step N 실행 (파일 생성)

- **Step 1 (Phase 0)**  
  - `saas_foundation.json`, `saas_implementation.json` 등 표준 2개를  
    복사하거나, 기술 스택 등만 조정해서 `.cursor/context/` 에 씁니다.
- **Step 2 (Phase 1)**  
  - Step 0에서 받은 정보로  
    `project_context.json`, `persona_context.json`, `scope_context.json` (🔴 3개)를 **새로 작성**하고,  
    나머지는 표준에서 복사/조정해서 같은 폴더에 씁니다.
- **Step 3 이후**  
  - 나머지 Context JSON들을 같은 방식으로 생성해  
    **총 17개**가 `.cursor/context/` 에 들어가도록 **Write** 도구로 파일을 만듭니다.

즉, **context, rule, skill만 있는 상태**에서는  
"프로젝트 초안"을 **Context 17개 생성**으로 해석하고, 위와 같은 절차로 진행됩니다.

---

## 6. (선택) "초안"을 코드 구조까지로 해석하는 경우

- "프로젝트 초안"을 **실제 디렉터리/코드 뼈대**까지 의미한다고 보면:
  - **context-generator만으로는 끝나지 않고**,
  - 에이전트가 **rule(CLAUDE.md)** 이나 **context(`saas_implementation.json`의 `project_structure`, `backend_file_order` 등)** 를 읽고,
  - **폴더 생성 + 초기 파일 생성**을 추가로 진행할 수 있습니다.
- 이때는 "스킬 하나만 타는 절차"가 아니라, **스킬 실행 후 rule/context를 참고한 추가 작업**으로 이어집니다.

---

## 요약

| 단계 | 내용 |
|------|------|
| 1 | 사용자 메시지 + rule + context + 스킬 목록(이름/경로/설명)만으로 시작 |
| 2 | 의미 매칭으로 context-generator 선택 |
| 3 | 해당 스킬 파일(SKILL.md)을 Read 해서 절차 확인 |
| 4 | Step 0(정보 수집) → Step 1~N(17개 Context JSON 생성) 순서로 진행 |
| 5 | (선택) "초안"을 코드 구조까지로 해석하면 rule/context 참고 후 디렉터리·파일 생성 추가 |