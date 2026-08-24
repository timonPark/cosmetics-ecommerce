# fe-fix — FE 버그 수정 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 버그 재현 및 진단

- 이슈 본문에서 재현 조건 파악
- 관련 Component/Hook 탐색
- 원인 특정 후 사용자에게 진단 결과 보고
- 🚧 원인 불명 시: [병목] 원인 특정 불가 — 추가 정보 요청
- ▶ [버그 진단] 시작 / ✅ [버그 진단] 원인: {파일:라인} 출력

## Step 2 — fe-dev 스킬 실행

- `.claude/commands/fe-dev.md` Read 후 직접 실행
- 수정 범위 최소화
- ▶ [fe-dev] 수정 시작 / ✅ [fe-dev] 수정 완료 출력

## Step 3 — codex-review 스킬 실행

- `.claude/commands/codex-review.md` Read 후 직접 실행
- 변경된 파일 대상으로 코드 리뷰 실행
- ▶ [codex-review] 시작 / ✅ [codex-review] 리뷰 결과 수신 완료

## Step 4 — 코드 리뷰 검토 및 반영

- 리뷰 항목별 반영 여부 판단:
  - 버그·렌더링 오류·레이어 규칙 위반 → 반드시 반영
  - 스타일·네이밍 → 프로젝트 코딩 규칙(`docs/coding-standards.md`)과 대조 후 판단
  - 설계 의견 → 사용자 확인 후 반영 여부 결정
- 반영 완료 후 변경 내용 사용자에게 보고
- ▶ [리뷰 반영] 시작 / ✅ [리뷰 반영] 반영 항목 목록 출력

## Step 5 — tdd-fe 스킬 실행

- `.claude/commands/tdd-fe.md` Read 후 직접 실행
- 버그 재현 실패 테스트 먼저 작성 → 수정 후 통과 확인
- ▶ [tdd-fe] 시작 / ✅ [tdd-fe] 테스트 통과 출력

## Step 6 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 7 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/fix: {수정 내용} closes #이슈번호"`
