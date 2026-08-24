# 태스크 1: BE 에이전트 4개

**산출물:** `.claude/agents/be-feat.md`, `be-fix.md`, `be-refactor.md`, `be-perf.md`

---

## be-feat — BE 신규 기능

Step 순서: 이슈 분석 → brainstorm → write-plan → be-dev → codex-review → 리뷰 반영 → tdd-be → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 이슈 분석 | Actions/Service/Repository 대상 레이어 특정, 기존 유사 코드 탐색 |
| brainstorm | Architectural 경로, 스펙 문서 `docs/specs/` 커밋 |
| write-plan | 계획 문서 `docs/plans/` 커밋 |
| be-dev | Actions → Service → Repository 순서 구현, 레이어별 커밋 |
| codex-review | Codex CLI로 교차 검증, 결과 `code-review/{브랜치명}/code-review.md` 저장 |
| 리뷰 반영 | Critical/Major → 반드시 반영, 설계 의견 → 사용자 확인 |
| tdd-be | Service 단위 테스트 → Repository 통합 테스트 |
| 검증 | `npx tsc --noEmit` + `pnpm test` 통과 |
| 커밋 | 사용자 명시적 승인 후 `BE/feat: {내용} closes #이슈번호` |

---

## be-fix — BE 버그 수정

Step 순서: 버그 진단 → be-dev → codex-review → 리뷰 반영 → tdd-be → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 버그 진단 | 재현 조건 파악, 원인 레이어:라인 특정, 사용자 보고 |
| be-dev | 수정 범위 최소화 — 원인 레이어만 수정 |
| codex-review | 교차 검증 |
| 리뷰 반영 | 반영 여부 판단 |
| tdd-be | 버그 재현 실패 테스트 먼저 → 수정 후 통과 확인 |
| 검증 | `npx tsc --noEmit` + `pnpm test` 통과 |
| 커밋 | `BE/fix: {내용} closes #이슈번호` |

---

## be-refactor — BE 리팩토링

Step 순서: 이슈 분석 → brainstorm → be-dev → codex-review → 리뷰 반영 → tdd-be → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 이슈 분석 | 레이어 위반·책임 혼재 등 문제점 파악 |
| brainstorm | 동작 변경 없음 보장 전략 수립 |
| be-dev | 기능 변경 없이 구조만 변경, 단계별 커밋 |
| codex-review | 교차 검증 |
| 리뷰 반영 | 반영 여부 판단 |
| tdd-be | 기존 테스트 전부 통과 확인 (동작 변경 없음 검증) |
| 검증 | `npx tsc --noEmit` + `pnpm test` 통과 |
| 커밋 | `BE/refactor: {내용} closes #이슈번호` |

---

## be-perf — BE 성능 개선

Step 순서: 성능 분석 → be-dev → codex-review → 리뷰 반영 → tdd-be → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 성능 분석 | 병목 지점(쿼리/이미지 처리) 특정, 현재 상태 기록 |
| be-dev | 쿼리 최적화 또는 이미지 처리 성능 개선 |
| codex-review | 교차 검증 |
| 리뷰 반영 | 반영 여부 판단 |
| tdd-be | 기존 동작 보장 테스트 확인 |
| 검증 | `npx tsc --noEmit` + `pnpm test` + 개선 결과 사용자 보고 |
| 커밋 | `BE/perf: {내용} closes #이슈번호` |
