# fe-perf — FE 성능 개선 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 성능 측정 및 분석

- 렌더링 병목 또는 번들 크기 문제 파악
- 관련 Component/Hook 탐색
- ▶ [성능 분석] 시작 / ✅ [성능 분석] 병목: {파일:라인} 출력

## Step 2 — fe-dev 스킬 실행

- `.claude/commands/fe-dev.md` Read 후 직접 실행
- 렌더링 최적화 또는 번들 최적화 구현
- ▶ [fe-dev] 시작 / ✅ [fe-dev] 성능 개선 구현 완료 출력

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
- 기존 동작 보장 테스트 확인
- ▶ [tdd-fe] 시작 / ✅ [tdd-fe] 테스트 통과 출력

## Step 6 — 검증

```bash
npx tsc --noEmit
pnpm test
```

- 성능 개선 결과 사용자에게 보고

## Step 7 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/perf: {내용} closes #이슈번호"`
