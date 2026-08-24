# dev-harness 스킬 구현 계획

**목표:** GitHub 이슈 번호를 입력받아 작업 유형을 분류하고 해당 에이전트 스펙을 Read해 Claude가 직접 단계별로 실행하는 개발 워크플로우 오케스트레이터와 10개 에이전트 파일 구현

**아키텍처:** dev-harness가 오케스트레이터로 이슈 분류 후 `.claude/agents/` 하위 에이전트 파일을 Read해 직접 실행한다. Agent 툴 호출 없이 Claude가 단계별로 수행하며, 각 에이전트는 기존 스킬(brainstorm, write-plan, be-dev, fe-dev, tdd-be, tdd-fe)을 체인으로 구성한다.

**기술 스택:** Markdown 스킬 파일, gh CLI, git

**스펙:** `docs/specs/2026-08-24-dev-harness-design.md`

## 전역 제약

- `.claude/commands/` 파일은 cp 방식으로만 생성 (classifier 차단 우회)
- `.claude/agents/` 디렉토리는 새로 생성
- 모든 에이전트는 Agent 툴 호출 금지 — Claude가 스펙을 Read 후 직접 실행
- 커밋은 사용자 명시적 승인 후에만 실행
- 시간은 KST(UTC+9) 기준

---

### 태스크 1: `.claude/agents/` 디렉토리 및 BE 에이전트 파일 4개

**파일:**
- 생성: `.claude/agents/be-feat.md`
- 생성: `.claude/agents/be-fix.md`
- 생성: `.claude/agents/be-refactor.md`
- 생성: `.claude/agents/be-perf.md`

**인터페이스:**
- 소비: 없음 (신규 파일)
- 생산: dev-harness가 Read해서 실행하는 에이전트 스펙

- [ ] **스텝 1: `.claude/agents/` 디렉토리 생성**

```bash
mkdir -p .claude/agents
```

- [ ] **스텝 2: `be-feat.md` 작성**

```markdown
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

## Step 5 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- Service 단위 테스트 → Repository 통합 테스트 순서
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 테스트 통과 확인 출력

## Step 6 — 검증

```bash
npx tsc --noEmit
pnpm test
```

- 두 명령 모두 통과 확인
- ✅ [검증] tsc PASS / pnpm test PASS 출력

## Step 7 — 커밋

- 사용자 명시적 승인("커밋해주세요") 후에만 실행
- `git commit -m "BE/feat: {작업 내용} closes #이슈번호"`
```

- [ ] **스텝 3: `be-fix.md` 작성**

```markdown
# be-fix — BE 버그 수정 에이전트

**Agent 툴 호출 금지.** 각 스킬은 해당 스킬 파일을 Read 후 Claude가 직접 실행한다.

## Step 1 — 버그 재현 및 진단

- 이슈 본문에서 재현 조건 파악
- 관련 Actions/Service/Repository 코드 탐색
- 원인 특정 후 사용자에게 진단 결과 보고
- 🚧 원인 불명 시: [병목] 원인 특정 불가 — 추가 정보 요청
- ▶ [버그 진단] 시작 / ✅ [버그 진단] 원인: {파일:라인} 출력

## Step 2 — be-dev 스킬 실행

- `.claude/commands/be-dev.md` Read 후 직접 실행
- 수정 범위 최소화 — 원인 레이어만 수정
- ▶ [be-dev] 수정 시작 / ✅ [be-dev] 수정 완료 출력

## Step 3 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- 버그 재현하는 실패 테스트 먼저 작성 → 수정 후 통과 확인
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 테스트 통과 확인 출력

## Step 4 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 5 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "BE/fix: {수정 내용} closes #이슈번호"`
```

- [ ] **스텝 4: `be-refactor.md` 작성**

```markdown
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

## Step 4 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- 기존 테스트 전부 통과 확인 (동작 변경 없음 검증)
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 기존 테스트 전부 통과 출력

## Step 5 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 6 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "BE/refactor: {내용} closes #이슈번호"`
```

- [ ] **스텝 5: `be-perf.md` 작성**

```markdown
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

## Step 3 — tdd-be 스킬 실행

- `.claude/commands/tdd-be.md` Read 후 직접 실행
- 기존 동작 보장 테스트 확인
- ▶ [tdd-be] 시작 / ✅ [tdd-be] 테스트 통과 출력

## Step 4 — 검증

```bash
npx tsc --noEmit
pnpm test
```

- 개선 결과 사용자에게 보고 (변경 전후 비교)

## Step 5 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "BE/perf: {내용} closes #이슈번호"`
```

- [ ] **스텝 6: 커밋**

```bash
git add .claude/agents/be-feat.md .claude/agents/be-fix.md .claude/agents/be-refactor.md .claude/agents/be-perf.md
git commit -m "공통/docs: BE 에이전트 파일 4개 작성 (be-feat, be-fix, be-refactor, be-perf)"
```

---

### 태스크 2: FE 에이전트 파일 4개

**파일:**
- 생성: `.claude/agents/fe-feat.md`
- 생성: `.claude/agents/fe-fix.md`
- 생성: `.claude/agents/fe-style.md`
- 생성: `.claude/agents/fe-perf.md`

**인터페이스:**
- 소비: 없음 (신규 파일)
- 생산: dev-harness가 Read해서 실행하는 에이전트 스펙

- [ ] **스텝 1: `fe-feat.md` 작성**

```markdown
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

## Step 5 — tdd-fe 스킬 실행

- `.claude/commands/tdd-fe.md` Read 후 직접 실행
- Component 단위 테스트 → Hook 단위 테스트 순서
- ▶ [tdd-fe] 시작 / ✅ [tdd-fe] 테스트 통과 확인 출력

## Step 6 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 7 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/feat: {작업 내용} closes #이슈번호"`
```

- [ ] **스텝 2: `fe-fix.md` 작성**

```markdown
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

## Step 3 — tdd-fe 스킬 실행

- `.claude/commands/tdd-fe.md` Read 후 직접 실행
- 버그 재현 실패 테스트 먼저 작성 → 수정 후 통과 확인
- ▶ [tdd-fe] 시작 / ✅ [tdd-fe] 테스트 통과 출력

## Step 4 — 검증

```bash
npx tsc --noEmit
pnpm test
```

## Step 5 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/fix: {수정 내용} closes #이슈번호"`
```

- [ ] **스텝 3: `fe-style.md` 작성**

```markdown
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

## Step 3 — 검증

```bash
npx tsc --noEmit
```

- 시각적 결과 사용자 확인 요청

## Step 4 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/style: {내용} closes #이슈번호"`
```

- [ ] **스텝 4: `fe-perf.md` 작성**

```markdown
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

## Step 3 — tdd-fe 스킬 실행

- `.claude/commands/tdd-fe.md` Read 후 직접 실행
- 기존 동작 보장 테스트 확인
- ▶ [tdd-fe] 시작 / ✅ [tdd-fe] 테스트 통과 출력

## Step 4 — 검증

```bash
npx tsc --noEmit
pnpm test
```

- 성능 개선 결과 사용자에게 보고

## Step 5 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "FE/perf: {내용} closes #이슈번호"`
```

- [ ] **스텝 5: 커밋**

```bash
git add .claude/agents/fe-feat.md .claude/agents/fe-fix.md .claude/agents/fe-style.md .claude/agents/fe-perf.md
git commit -m "공통/docs: FE 에이전트 파일 4개 작성 (fe-feat, fe-fix, fe-style, fe-perf)"
```

---

### 태스크 3: 공통 에이전트 파일 2개

**파일:**
- 생성: `.claude/agents/common-docs.md`
- 생성: `.claude/agents/common-chore.md`

**인터페이스:**
- 소비: 없음 (신규 파일)
- 생산: dev-harness가 Read해서 실행하는 에이전트 스펙

- [ ] **스텝 1: `common-docs.md` 작성**

```markdown
# common-docs — 공통 문서 작업 에이전트

**Agent 툴 호출 금지.**

## Step 1 — 이슈 분석

- 작성/수정할 문서 파악
- 관련 기존 문서 확인
- ▶ [이슈 분석] 시작 / ✅ [이슈 분석] {대상 문서 목록} 출력

## Step 2 — 문서 작성

- 이슈 요구사항에 맞게 문서 작성 또는 수정
- CLAUDE.md 330줄 제한 준수 (초과 시 `@파일경로` 분리)
- `.claude/commands/` 파일은 docs/ 경유 cp 방식으로 생성
- ▶ [문서 작성] 시작 / ✅ [문서 작성] 완료 출력

## Step 3 — 사용자 확인

- 작성된 내용 사용자에게 검토 요청

## Step 4 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "공통/docs: {내용} closes #이슈번호"`
```

- [ ] **스텝 2: `common-chore.md` 작성**

```markdown
# common-chore — 공통 환경 설정 에이전트

**Agent 툴 호출 금지.**

## Step 1 — 이슈 분석

- 설정 변경 범위 파악
- 영향 받는 파일/환경 확인
- ▶ [이슈 분석] 시작 / ✅ [이슈 분석] {변경 대상} 출력

## Step 2 — (필요시) brainstorm 스킬 실행

- 복잡한 환경 설정인 경우 `.claude/commands/brainstorm.md` Read 후 실행
- 단순 패키지 설치·설정 변경은 SKIP
- ▶ [brainstorm] 시작 / ✅ [brainstorm] 스펙 저장 경로 출력

## Step 3 — 환경 설정 작업

- 패키지 설치, 설정 파일 수정 등
- 단계별 커밋 (사용자 승인 후)
- ▶ [환경 설정] 시작 / ✅ [환경 설정] 완료 출력

## Step 4 — 검증

- 설정 적용 확인 (`pnpm build` 또는 `pnpm dev` 실행)
- ✅ [검증] 빌드/실행 정상 확인 출력

## Step 5 — 커밋

- 사용자 명시적 승인 후 실행
- `git commit -m "공통/chore: {내용} closes #이슈번호"`
```

- [ ] **스텝 3: 커밋**

```bash
git add .claude/agents/common-docs.md .claude/agents/common-chore.md
git commit -m "공통/docs: 공통 에이전트 파일 2개 작성 (common-docs, common-chore)"
```

---

### 태스크 4: dev-harness 오케스트레이터

**파일:**
- 생성: `docs/github-project-draft.md` (임시 — cp 후 `.claude/commands/dev-harness.md`로 이동)

**인터페이스:**
- 소비: `.claude/agents/` 하위 10개 에이전트 파일
- 생산: `/dev-harness #이슈번호` 명령으로 전체 워크플로우 실행

- [ ] **스텝 1: `docs/dev-harness-draft.md` 작성**

```markdown
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

/dev-harness #이슈번호

## 투명성 원칙

모든 단계 시작·완료·병목 시 아래 형식으로 출력한다.

- 단계 시작: ▶ [단계명] {하려는 작업 한 줄 설명}
- 단계 완료: ✅ [단계명] {완료 결과 한 줄 요약}
- 병목 발생: 🚧 [병목] {상황 설명} — 어떻게 진행할까요?

각 에이전트 실행 시 진행 상태 표를 출력한다:

| 단계 | 상태 |
|---|---|
| Step 1 — 이슈 분석 | ✅ 완료 |
| Step 2 — brainstorm | ▶ 진행 중 |
| Step 3 — write-plan | ⬜ 대기 |

## Step 1 — 이슈 조회

gh issue view {이슈번호} --repo timonPark/cosmetics-ecommerce

제목, 라벨, 본문 확인 후 Step 2 진행.

## Step 2 — 작업 유형 분류

이슈 제목의 {도메인}/{식별값} 패턴으로 분류한다.
분류 우선순위: 이슈 제목 → 라벨 → 본문 → AskUserQuestion

| 도메인/식별값 | 에이전트 파일 |
|---|---|
| BE/feat | .claude/agents/be-feat.md |
| BE/fix | .claude/agents/be-fix.md |
| BE/refactor | .claude/agents/be-refactor.md |
| BE/perf | .claude/agents/be-perf.md |
| FE/feat | .claude/agents/fe-feat.md |
| FE/fix | .claude/agents/fe-fix.md |
| FE/style | .claude/agents/fe-style.md |
| FE/perf | .claude/agents/fe-perf.md |
| 공통/docs | .claude/agents/common-docs.md |
| 공통/chore | .claude/agents/common-chore.md |

분류 결과를 사용자에게 보고 후 Step 3 진행.

## Step 3 — 작업 준비

1. feature 브랜치 생성:
   git checkout -b feature/#이슈번호-작업명 dev

2. work_history 파일 생성:
   work_history/YYYY-MM-DD-feature-#이슈번호-작업명.md

3. GitHub Project Status → In Progress:
   gh api graphql로 timonPark/projects/11 Status 변경

## Step 4 — 에이전트 실행

Agent 툴 호출 금지. 해당 에이전트 파일을 Read 후 Claude가 단계별 직접 실행한다.

Read: .claude/agents/{에이전트파일}.md
→ 파일 내 Step 순서대로 직접 실행

## Step 5 — 완료 처리

1. git push origin feature/#이슈번호-작업명
2. PR 생성:
   gh pr create --base dev --title "{도메인}/{식별값}: {작업내용}" --body "closes #이슈번호"
3. PR 머지 (사용자 승인 후):
   gh pr merge {PR번호} --merge --delete-branch
4. GitHub Project Status → Done
5. work_history PR URL·머지 완료일(KST) 업데이트
```

- [ ] **스텝 2: 사용자에게 cp 요청**

```
cp docs/dev-harness-draft.md .claude/commands/dev-harness.md
```

- [ ] **스텝 3: add 명령어 안내 후 커밋**

```bash
# 사용자가 git add .claude/commands/dev-harness.md 실행 후
git commit -m "공통/docs: dev-harness 오케스트레이터 스킬 작성 closes #27"
git push origin feature/#27-dev-harness
```

- [ ] **스텝 4: PR 생성**

```bash
gh pr create \
  --repo timonPark/cosmetics-ecommerce \
  --base dev \
  --head feature/#27-dev-harness \
  --title "공통/docs: 개발 하네스 스킬 작성" \
  --body "closes #27"
```
