# Cursor Skills 등록 가이드

프로젝트 스킬은 `.cursor/skills/{name}/SKILL.md` 형식으로 저장하면 Cursor가 자동 인식합니다.

---

## 등록된 Skills

| Skill | 경로 | 용도 | Phase |
|-------|------|------|-------|
| `module-generator` | `.cursor/skills/module-generator/SKILL.md` | 비즈니스 모듈 7개 파일 표준 패턴 생성 | Phase 3 |
| `context-generator` | `.cursor/skills/context-generator/SKILL.md` | 새 프로젝트 Context JSON 17개 생성 | Phase 0~2 |
| `governance-checker` | `.cursor/skills/governance-checker/SKILL.md` | 모듈별 거버넌스 표준 준수 검사 (6개 카테고리, 28개 항목) | Phase 3~4 |
| `frontend-generator` | `.cursor/skills/frontend-generator/SKILL.md` | React 페이지 + Client 컴포넌트 + useAgent 훅 표준 패턴 생성 | Phase 3 |
| `migration-generator` | `.cursor/skills/migration-generator/SKILL.md` | models.py 기반 Alembic DB 마이그레이션 자동 생성 | Phase 3 |
| `test-scenario-generator` | `.cursor/skills/test-scenario-generator/SKILL.md` | Agent 시뮬레이션 테스트 시나리오 자동 생성 (6개 카테고리) | Phase 4 |
| `simulation-runner` | `.cursor/skills/simulation-runner/SKILL.md` | Phase 4 전체 시뮬레이션 실행 + Evaluation Report + G-07 Gate 준비 | Phase 4 |
| `deploy-runner` | `.cursor/skills/deploy-runner/SKILL.md` | Phase 5 배포 파이프라인 + Monitor-A + KPI + G-08 Release Gate | Phase 5 |
| `evolution-runner` | `.cursor/skills/evolution-runner/SKILL.md` | Phase 6 Evolution Loop + Evol-A + Drift 분석 + G-09 Gate | Phase 6 |

---

## Skills 사용 흐름

```
새 프로젝트 시작 시:
  context-generator  →  Context 17개 JSON 생성 (Phase 0~2)
       ↓
  module-generator   →  백엔드 모듈 7개 파일 생성 (Phase 3)
       ↓
  migration-generator →  Alembic DB 마이그레이션 생성 (Phase 3)
       ↓
  frontend-generator  →  React 프론트엔드 페이지 생성 (Phase 3)
       ↓
  governance-checker  →  거버넌스 표준 준수 검사 (Phase 3~4)
       ↓
  test-scenario-generator → Agent 테스트 시나리오 생성 (Phase 4)
       ↓
  simulation-runner     → 전체 시뮬레이션 실행 + Evaluation Report (Phase 4)
       ↓
  deploy-runner         → Docker 배포 + Monitor-A + KPI + G-08 Gate (Phase 5)
       ↓
  evolution-runner      → Evolution Loop + Evol-A + Drift 분석 + G-09 Gate (Phase 6)
```

---

## Skill 작성 규칙

- 파일 위치: `.cursor/skills/{name}/SKILL.md`
- Frontmatter: `name`, `description` 필수
- 트리거 키워드: description에 한국어 + 영어 포함
- Reference Files: 참조할 실제 프로젝트 파일 경로 명시
