# be-perf — BE 성능 개선 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 성능 측정 및 분석

- 이슈 본문에서 병목 지점 파악 (쿼리, 이미지 처리 등)
- 관련 코드 탐색, 현재 쿼리/로직 분석
- ▶ [성능 분석] 시작 / ✅ [성능 분석] 병목: {파일:라인} 출력

## Step 2 — be-dev 스킬 실행

- `.claude/commands/be-dev.md` Read 후 직접 실행
- 쿼리 최적화 또는 이미지 처리 성능 개선 구현
- ▶ [be-dev] 시작 / ✅ [be-dev] 성능 개선 구현 완료 출력

## Step 3 — codex-review 스킬 실행

- `.claude/commands/codex-review.md` Read 후 직접 실행
- 변경된 파일 대상으로 코드 리뷰 실행
- ▶ [codex-review] 시작 / ✅ [codex-review] 리뷰 결과 수신 완료

## Step 4 — 코드 리뷰 검토 및 반영

- 리뷰 항목별 반영 여부 판단:
  - 버그·보안 취약점·레이어 규칙 위반 → 반드시 반영
  - 스타일·네이밍 → 프로젝트 코딩 규칙(`docs/coding-standards.md`)과 대조 후 판단
  - 설계 의견 → 사용자 확인 후 반영 여부 결정
- 반영 완료 후 변경 내용 사용자에게 보고
- ▶ [리뷰 반영] 시작 / ✅ [리뷰 반영] 반영 항목 목록 출력

## Step 5 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- 기존 동작 보장 테스트 확인
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 테스트 통과 출력

## Step 6 — 검증

```bash
npx tsc --noEmit
pnpm test
```

- 개선 결과 사용자에게 보고 (변경 전후 비교)

## Step 7 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "BE/perf: {내용} closes #이슈번호"`
