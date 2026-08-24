# be-refactor — BE 리팩토링 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 이슈 분석

- 리팩토링 대상 코드 탐색
- 현재 구조의 문제점 파악 (레이어 위반, 책임 혼재 등)
- ▶ [이슈 분석] 시작 / ✅ [이슈 분석] 문제점 목록 출력

## Step 2 — brainstorm 스킬 실행

- `.claude/commands/brainstorm.md` Read 후 직접 실행
- 리팩토링 방향 설계, 동작 변경 없음 보장 전략 수립
- ▶ [brainstorm] 시작 / ✅ [brainstorm] 스펙 저장 경로 출력

## Step 3 — be-dev 스킬 실행

- `.claude/commands/be-dev.md` Read 후 직접 실행
- 기능 변경 없이 구조만 변경, 단계별 커밋
- ▶ [be-dev] 시작 / ✅ [be-dev] 리팩토링 완료 출력

## Step 4 — review 스킬 실행

- `.claude/commands/review.md` Read 후 직접 실행
- 변경된 파일 대상으로 코드 리뷰 실행
- ▶ [코드 리뷰] 시작 / ✅ [코드 리뷰] 리뷰 결과 수신 완료

## Step 5 — 코드 리뷰 검토 및 반영

- 리뷰 항목별 반영 여부 판단:
  - 버그·보안 취약점·레이어 규칙 위반 → 반드시 반영
  - 스타일·네이밍 → 프로젝트 코딩 규칙(`docs/coding-standards.md`)과 대조 후 판단
  - 설계 의견 → 사용자 확인 후 반영 여부 결정
- 반영 완료 후 변경 내용 사용자에게 보고
- ▶ [리뷰 반영] 시작 / ✅ [리뷰 반영] 반영 항목 목록 출력

## Step 6 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- 기존 테스트 전부 통과 확인 (동작 변경 없음 검증)
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 기존 테스트 전부 통과 출력

## Step 7 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 8 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "BE/refactor: {내용} closes #이슈번호"`
