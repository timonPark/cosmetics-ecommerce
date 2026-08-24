# be-feat — BE 신규 기능 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 이슈 분석

- 이슈 본문 재확인, 구현 대상 레이어(Actions/Service/Repository) 특정
- 관련 기존 파일 탐색 (`src/actions/`, `src/services/`, `src/repositories/`)
- ▶ [이슈 분석] 시작 / ✅ [이슈 분석] {대상 레이어 및 파일 목록} 출력

## Step 2 — brainstorm 스킬 실행

- `.claude/commands/brainstorm.md` Read 후 직접 실행
- Architectural 경로 — 스펙 문서 작성 및 `docs/specs/` 커밋 포함
- ▶ [brainstorm] 시작 / ✅ [brainstorm] 스펙 저장 경로 출력

## Step 3 — write-plan 스킬 실행

- `.claude/commands/write-plan.md` Read 후 직접 실행
- 계획 문서 `docs/plans/` 커밋 포함
- ▶ [write-plan] 시작 / ✅ [write-plan] 계획 저장 경로 출력

## Step 4 — be-dev 스킬 실행

- `.claude/commands/be-dev.md` Read 후 직접 실행
- Actions → Service → Repository 순서 구현
- 각 레이어 완료 시 커밋 (사용자 승인 후)
- ▶ [be-dev] {현재 레이어} 시작 / ✅ [be-dev] {레이어} 완료 출력

## Step 5 — codex-review 스킬 실행

- `.claude/commands/codex-review.md` Read 후 직접 실행
- 변경된 파일 대상으로 코드 리뷰 실행
- ▶ [codex-review] 시작 / ✅ [codex-review] 리뷰 결과 수신 완료

## Step 6 — 코드 리뷰 검토 및 반영

- 리뷰 항목별 반영 여부 판단:
  - 버그·보안 취약점·레이어 규칙 위반 → 반드시 반영
  - 스타일·네이밍 → 프로젝트 코딩 규칙(`docs/coding-standards.md`)과 대조 후 판단
  - 설계 의견 → 사용자 확인 후 반영 여부 결정
- 반영 완료 후 변경 내용 사용자에게 보고
- ▶ [리뷰 반영] 시작 / ✅ [리뷰 반영] 반영 항목 목록 출력

## Step 7 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- Service 단위 테스트 → Repository 통합 테스트 순서
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 테스트 통과 확인 출력

## Step 8 — 검증

```bash
npx tsc --noEmit
pnpm test
```

- 두 명령 모두 통과 확인
- ✅ [검증] tsc PASS / pnpm test PASS 출력

## Step 9 — 커밋

- 사용자 명시적 승인("커밋해주세요") 후에만 실행
- `git commit -m "BE/feat: {작업 내용} closes #이슈번호"`
