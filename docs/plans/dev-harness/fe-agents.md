# 태스크 2: FE 에이전트 4개

**산출물:** `.claude/agents/fe-feat.md`, `fe-fix.md`, `fe-style.md`, `fe-perf.md`

---

## fe-feat — FE 화면 기능 개발

Step 순서: 이슈 분석 → brainstorm → write-plan → fe-dev → codex-review → 리뷰 반영 → tdd-fe → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 이슈 분석 | 이슈 본문 + Figma 링크 확인, Page/Component/Hook 대상 특정 |
| brainstorm | 컴포넌트 구조 설계, 스펙 문서 커밋 |
| write-plan | 계획 문서 커밋 |
| fe-dev | Page → Component → Hook 순서 구현, 각 단위 완료 시 커밋 |
| codex-review | Codex CLI로 교차 검증 |
| 리뷰 반영 | 버그·렌더링 오류 → 반드시 반영, 설계 의견 → 사용자 확인 |
| tdd-fe | Component 단위 테스트 → Hook 단위 테스트 (코로케이션) |
| 검증 | `npx tsc --noEmit` + `pnpm test` 통과 |
| 커밋 | `FE/feat: {내용} closes #이슈번호` |

---

## fe-fix — FE 버그 수정

Step 순서: 버그 진단 → fe-dev → codex-review → 리뷰 반영 → tdd-fe → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 버그 진단 | 재현 조건 파악, 원인 Component/Hook 특정, 사용자 보고 |
| fe-dev | 수정 범위 최소화 |
| codex-review | 교차 검증 |
| 리뷰 반영 | 반영 여부 판단 |
| tdd-fe | 버그 재현 실패 테스트 먼저 → 수정 후 통과 확인 |
| 검증 | `npx tsc --noEmit` + `pnpm test` 통과 |
| 커밋 | `FE/fix: {내용} closes #이슈번호` |

---

## fe-style — FE 디자인/스타일 변경

Step 순서: 이슈 분석 → fe-dev → codex-review → 리뷰 반영 → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 이슈 분석 | Figma 링크 확인, 변경 대상 Component 파악 |
| fe-dev | Tailwind CSS / shadcn/ui 기반 스타일 변경 |
| codex-review | 교차 검증 (a11y 포함) |
| 리뷰 반영 | a11y 문제 → 반드시 반영, 설계 의견 → 사용자 확인 |
| 검증 | `npx tsc --noEmit` + 시각적 결과 사용자 확인 요청 |
| 커밋 | `FE/style: {내용} closes #이슈번호` |

---

## fe-perf — FE 성능 개선

Step 순서: 성능 분석 → fe-dev → codex-review → 리뷰 반영 → tdd-fe → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 성능 분석 | 렌더링 병목 또는 번들 크기 문제 파악 |
| fe-dev | 렌더링 최적화 또는 번들 최적화 구현 |
| codex-review | 교차 검증 |
| 리뷰 반영 | 반영 여부 판단 |
| tdd-fe | 기존 동작 보장 테스트 확인 |
| 검증 | `npx tsc --noEmit` + `pnpm test` + 개선 결과 사용자 보고 |
| 커밋 | `FE/perf: {내용} closes #이슈번호` |
