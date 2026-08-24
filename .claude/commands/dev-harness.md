---
name: dev-harness
description: "GitHub 이슈 번호를 입력받아 작업 유형 분류 후 해당 에이전트 스펙을 Read해 Claude가 직접 단계별 실행하는 개발 워크플로우 오케스트레이터"
allowed-tools:
  [
    'Read',
    'Write',
    'Edit',
    'Bash(git:*)',
    'Bash(gh:*)',
    'Bash(npx:*)',
    'Bash(pnpm:*)',
    'Bash(mkdir:*)',
    'AskUserQuestion',
    'mcp__ide__getDiagnostics',
  ]
---

# dev-harness

## 사용법

```
/dev-harness #이슈번호
```

## 투명성 원칙

모든 단계 시작·완료·병목 시 아래 형식으로 출력한다.

- 단계 시작: `▶ [단계명] {하려는 작업 한 줄 설명}`
- 단계 완료: `✅ [단계명] {완료 결과 한 줄 요약}`
- 병목 발생: `🚧 [병목] {상황 설명} — 어떻게 진행할까요?`

각 에이전트 실행 시 진행 상태 표를 출력한다:

| 단계 | 상태 |
|---|---|
| Step 1 — 이슈 분석 | ✅ 완료 |
| Step 2 — brainstorm | ▶ 진행 중 |
| Step 3 — write-plan | ⬜ 대기 |

## Step 1 — 이슈 조회

▶ [이슈 조회] 시작

```bash
gh issue view {이슈번호} --repo timonPark/cosmetics-ecommerce
```

제목, 라벨, 본문 확인 후 Step 2 진행.

✅ [이슈 조회] 제목·라벨·본문 확인 완료

## Step 2 — 작업 유형 분류

▶ [분류] 이슈 제목 패턴으로 에이전트 선택

이슈 제목의 `{도메인}/{식별값}` 패턴으로 분류한다.
분류 우선순위: 이슈 제목 → 라벨 → 본문 → AskUserQuestion

| 도메인/식별값 | 에이전트 파일 |
|---|---|
| BE/feat | `.claude/agents/be-feat.md` |
| BE/fix | `.claude/agents/be-fix.md` |
| BE/refactor | `.claude/agents/be-refactor.md` |
| BE/perf | `.claude/agents/be-perf.md` |
| FE/feat | `.claude/agents/fe-feat.md` |
| FE/fix | `.claude/agents/fe-fix.md` |
| FE/style | `.claude/agents/fe-style.md` |
| FE/perf | `.claude/agents/fe-perf.md` |
| 공통/docs | `.claude/agents/common-docs.md` |
| 공통/chore | `.claude/agents/common-chore.md` |

분류 결과를 사용자에게 보고 후 Step 3 진행.

✅ [분류] 에이전트: {에이전트파일명} 선택

## Step 3 — 작업 준비

▶ [작업 준비] 브랜치 생성 / work_history 생성 / Status 변경

1. feature 브랜치 생성:
   ```bash
   git checkout -b feature/#이슈번호-작업명 dev
   ```

2. work_history 파일 생성:
   `work_history/YYYY-MM-DD-feature-#이슈번호-작업명.md`
   (docs/work-history-spec.md 규격 준수)

3. GitHub Project Status → In Progress:
   ```bash
   gh api graphql -f query='
   mutation {
     updateProjectV2ItemFieldValue(input: {
       projectId: "PVT_kwHOAPKoTM4BhNl1"
       itemId: "{아이템ID}"
       fieldId: "PVTSSF_lAHOAPKoTM4BhNl1zhgKKvM"
       value: { singleSelectOptionId: "47fc9ee4" }
     }) { projectV2Item { id } }
   }'
   ```

✅ [작업 준비] 브랜치·work_history·Status 설정 완료

## Step 4 — 에이전트 실행

▶ [에이전트 실행] {에이전트파일명} Read 후 직접 실행

**Agent 툴 호출 금지.** 해당 에이전트 파일을 Read 후 Claude가 단계별 직접 실행한다.

```
Read: .claude/agents/{에이전트파일}.md
→ 파일 내 Step 순서대로 직접 실행
```

✅ [에이전트 실행] 모든 Step 완료

## Step 5 — 완료 처리

▶ [완료 처리] push / PR 생성 / Status Done / work_history 업데이트

1. push:
   ```bash
   git push origin feature/#이슈번호-작업명
   ```

2. PR 생성:
   ```bash
   gh pr create \
     --repo timonPark/cosmetics-ecommerce \
     --base dev \
     --title "{도메인}/{식별값}: {작업내용}" \
     --body "closes #이슈번호"
   ```

3. PR 머지 (사용자 승인 후):
   ```bash
   gh pr merge {PR번호} --merge --delete-branch
   ```

4. GitHub Project Status → Done:
   ```bash
   gh api graphql -f query='
   mutation {
     updateProjectV2ItemFieldValue(input: {
       projectId: "PVT_kwHOAPKoTM4BhNl1"
       itemId: "{아이템ID}"
       fieldId: "PVTSSF_lAHOAPKoTM4BhNl1zhgKKvM"
       value: { singleSelectOptionId: "98236657" }
     }) { projectV2Item { id } }
   }'
   ```

5. work_history PR URL·머지 완료일(KST) 업데이트

✅ [완료 처리] PR 머지·Status Done·work_history 업데이트 완료
