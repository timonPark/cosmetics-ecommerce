# fe-feat — FE 화면 기능 개발 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 이슈 분석

- 이슈 본문 및 Figma 링크 확인
- 관련 레이어(Page/Component/Hook) 특정
- ▶ [이슈 분석] 시작 / ✅ [이슈 분석] {대상 파일 목록} 출력

## Step 2 — brainstorm 스킬 실행

- `.claude/commands/brainstorm.md` Read 후 직접 실행
- 컴포넌트 구조 설계, 스펙 문서 커밋
- ▶ [brainstorm] 시작 / ✅ [brainstorm] 스펙 저장 경로 출력

## Step 3 — write-plan 스킬 실행

- `.claude/commands/write-plan.md` Read 후 직접 실행
- 계획 문서 커밋
- ▶ [write-plan] 시작 / ✅ [write-plan] 계획 저장 경로 출력

## Step 4 — fe-dev 스킬 실행

- `.claude/commands/fe-dev.md` Read 후 직접 실행
- Page → Component → Hook 순서 구현, 각 단위 완료 시 커밋
- ▶ [fe-dev] {현재 레이어} 시작 / ✅ [fe-dev] {레이어} 완료 출력

## Step 5 — review 스킬 실행

- `.claude/commands/review.md` Read 후 직접 실행
- 변경된 파일 대상으로 코드 리뷰 실행
- ▶ [코드 리뷰] 시작 / ✅ [코드 리뷰] 리뷰 결과 수신 완료

## Step 6 — 코드 리뷰 검토 및 반영

- 리뷰 항목별 반영 여부 판단:
  - 버그·렌더링 오류·레이어 규칙 위반 → 반드시 반영
  - 스타일·네이밍 → 프로젝트 코딩 규칙(`docs/coding-standards.md`)과 대조 후 판단
  - 설계 의견 → 사용자 확인 후 반영 여부 결정
- 반영 완료 후 변경 내용 사용자에게 보고
- ▶ [리뷰 반영] 시작 / ✅ [리뷰 반영] 반영 항목 목록 출력

## Step 7 — tdd-fe 스킬 실행

- `.claude/commands/tdd-fe.md` Read 후 직접 실행
- Component 단위 테스트 → Hook 단위 테스트 순서
- ▶ [tdd-fe] 시작 / ✅ [tdd-fe] 테스트 통과 확인 출력

## Step 8 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 9 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/feat: {작업 내용} closes #이슈번호"`
