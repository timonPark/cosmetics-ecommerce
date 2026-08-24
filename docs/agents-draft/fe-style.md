# fe-style — FE 디자인/스타일 변경 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 이슈 분석

- Figma 링크 확인 (있는 경우 디자인 확인)
- 변경 대상 Component 파악
- ▶ [이슈 분석] 시작 / ✅ [이슈 분석] {대상 Component 목록} 출력

## Step 2 — fe-dev 스킬 실행

- `.claude/commands/fe-dev.md` Read 후 직접 실행
- Tailwind CSS / shadcn/ui 기반 스타일 변경 구현
- ▶ [fe-dev] 시작 / ✅ [fe-dev] 스타일 변경 완료 출력

## Step 3 — codex-review 스킬 실행

- `.claude/commands/codex-review.md` Read 후 직접 실행
- 변경된 파일 대상으로 코드 리뷰 실행
- ▶ [codex-review] 시작 / ✅ [codex-review] 리뷰 결과 수신 완료

## Step 4 — 코드 리뷰 검토 및 반영

- 리뷰 항목별 반영 여부 판단:
  - 접근성(a11y) 문제·레이어 규칙 위반 → 반드시 반영
  - 스타일·네이밍 → 프로젝트 코딩 규칙(`docs/coding-standards.md`)과 대조 후 판단
  - 설계 의견 → 사용자 확인 후 반영 여부 결정
- 반영 완료 후 변경 내용 사용자에게 보고
- ▶ [리뷰 반영] 시작 / ✅ [리뷰 반영] 반영 항목 목록 출력

## Step 5 — 검증

```bash
npx tsc --noEmit
```

- 시각적 결과 사용자 확인 요청

## Step 6 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/style: {내용} closes #이슈번호"`
