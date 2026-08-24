# dev-harness 스킬 구현 계획

**목표:** GitHub 이슈 번호를 입력받아 작업 유형을 분류하고 해당 에이전트 스펙을 Read해 Claude가 직접 단계별로 실행하는 개발 워크플로우 오케스트레이터와 10개 에이전트 파일 구현

**아키텍처:** dev-harness가 오케스트레이터로 이슈 분류 후 `.claude/agents/` 하위 에이전트 파일을 Read해 직접 실행한다. Agent 툴 호출 없이 Claude가 단계별로 수행하며, 각 에이전트는 기존 스킬(brainstorm, write-plan, be-dev, fe-dev, tdd-be, tdd-fe, codex-review)을 체인으로 구성한다.

**기술 스택:** Markdown 스킬 파일, gh CLI, git, Codex CLI

**스펙:** `docs/specs/2026-08-24-dev-harness-design.md`

## 전역 제약

- `.claude/commands/` 및 `.claude/agents/` 파일은 docs/ 경유 cp 방식으로 생성
- 모든 에이전트는 Agent 툴 호출 금지 — Claude가 스펙을 Read 후 직접 실행
- 커밋은 사용자 명시적 승인 후에만 실행
- 시간은 KST(UTC+9) 기준

---

## 태스크 요약

| 태스크 | 산출물 | 상세 |
|---|---|---|
| 태스크 1 | BE 에이전트 4개 | `@docs/plans/dev-harness/be-agents.md` |
| 태스크 2 | FE 에이전트 4개 | `@docs/plans/dev-harness/fe-agents.md` |
| 태스크 3 | 공통 에이전트 2개 + codex-review | `@docs/plans/dev-harness/common-and-review.md` |
| 태스크 4 | dev-harness 오케스트레이터 | `@docs/plans/dev-harness/orchestrator.md` |

---

## 구현 결과

| 파일 | 상태 |
|---|---|
| `.claude/agents/be-feat.md` | ✅ |
| `.claude/agents/be-fix.md` | ✅ |
| `.claude/agents/be-refactor.md` | ✅ |
| `.claude/agents/be-perf.md` | ✅ |
| `.claude/agents/fe-feat.md` | ✅ |
| `.claude/agents/fe-fix.md` | ✅ |
| `.claude/agents/fe-style.md` | ✅ |
| `.claude/agents/fe-perf.md` | ✅ |
| `.claude/agents/common-docs.md` | ✅ |
| `.claude/agents/common-chore.md` | ✅ |
| `.claude/commands/dev-harness.md` | ✅ |
| `.claude/commands/codex-review.md` | ✅ |
| `.agents/skills/code-review/SKILL.md` | ✅ |
