# dev-harness 스킬 설계 문서

**목표**: GitHub 이슈 번호를 입력받아 작업 유형을 분류하고, 해당 에이전트 스펙을 Read해 Claude가 직접 단계별로 실행하는 개발 워크플로우 오케스트레이터

**참고**: cdp-server의 work-manager 스킬 컨셉을 이 프로젝트에 맞게 재설계

---

## 파일 구조

```
.claude/
├── commands/
│   ├── dev-harness.md        # 오케스트레이터 스킬
│   └── codex-review.md       # Codex AI 교차 검증 스킬
├── agents/
│   ├── be-feat.md            # BE 신규 기능
│   ├── be-fix.md             # BE 버그 수정
│   ├── be-refactor.md        # BE 리팩토링
│   ├── be-perf.md            # BE 성능 개선
│   ├── fe-feat.md            # FE 화면 기능 개발
│   ├── fe-fix.md             # FE 버그 수정
│   ├── fe-style.md           # FE 디자인/스타일 변경
│   ├── fe-perf.md            # FE 성능 개선
│   ├── common-docs.md        # 공통 문서 작업
│   └── common-chore.md       # 공통 환경 설정
└── .agents/
    └── skills/code-review/SKILL.md  # Codex용 리뷰 스킬
```

---

## dev-harness 오케스트레이터

### 입력

```
/dev-harness #이슈번호
```

### 실행 흐름

**Step 1 — 이슈 조회**
- `gh issue view {이슈번호}` 실행
- 제목, 라벨, 본문 확인

**Step 2 — 작업 유형 분류**
- 이슈 제목의 `{도메인}/{식별값}` 패턴으로 분류
- 분류 우선순위: 이슈 제목 → 라벨 → 본문 → 사용자 확인(`AskUserQuestion`)

| 도메인/식별값 | 에이전트 파일 |
|---|---|
| `BE/feat` | `.claude/agents/be-feat.md` |
| `BE/fix` | `.claude/agents/be-fix.md` |
| `BE/refactor` | `.claude/agents/be-refactor.md` |
| `BE/perf` | `.claude/agents/be-perf.md` |
| `FE/feat` | `.claude/agents/fe-feat.md` |
| `FE/fix` | `.claude/agents/fe-fix.md` |
| `FE/style` | `.claude/agents/fe-style.md` |
| `FE/perf` | `.claude/agents/fe-perf.md` |
| `공통/docs` | `.claude/agents/common-docs.md` |
| `공통/chore` | `.claude/agents/common-chore.md` |

**Step 3 — 작업 준비**
- feature 브랜치 생성: `git checkout -b feature/#이슈번호-작업명 dev`
- `work_history/YYYY-MM-DD-{브랜치명}.md` 파일 생성
- GitHub Project Status → `In Progress`

**Step 4 — 에이전트 실행**
- **Agent 툴 호출 금지**. 해당 에이전트 파일을 Read 후 Claude가 단계별 직접 실행
- 각 단계 시작 시 진행 상태 표 출력

**Step 5 — 완료 처리**
- `git push origin {브랜치명}` 후 PR 생성
- GitHub Project Status → `Done`
- work_history PR URL·머지 완료일 업데이트

---

## 에이전트 공통 단계 구조

모든 에이전트는 아래 패턴을 따른다. 에이전트 유형에 따라 일부 단계가 생략된다.

| 단계 | 내용 | BE feat/refactor | BE fix/perf | FE feat | FE fix/style/perf | 공통 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 이슈 분석 / 버그 진단 | 대상 파악 | ✅ | ✅ | ✅ | ✅ | ✅ |
| brainstorm | 설계 브레인스토밍 | ✅ | — | ✅ | — | 선택 |
| write-plan | 구현 계획 | ✅ | — | ✅ | — | — |
| be-dev / fe-dev | 코드 구현 | ✅ | ✅ | ✅ | ✅ | ✅ |
| codex-review | AI 교차 검증 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 리뷰 검토·반영 | 반영 여부 판단 | ✅ | ✅ | ✅ | ✅ | ✅ |
| tdd-be / tdd-fe | 테스트 작성 | ✅ | ✅ | ✅ | ✅(fe) | — |
| 검증 | tsc + pnpm test | ✅ | ✅ | ✅ | ✅ | ✅ |
| 커밋 | 사용자 승인 후 | ✅ | ✅ | ✅ | ✅ | ✅ |

각 에이전트 상세 스펙: `@.claude/agents/`

---

## 투명성 원칙

dev-harness 및 모든 에이전트는 아래 형식으로 진행 상황을 출력한다.

- 단계 시작: `▶ [단계명] {하려는 작업 한 줄 설명}`
- 단계 완료: `✅ [단계명] {완료 결과 한 줄 요약}`
- 병목 발생: `🚧 [병목] {상황 설명} — 어떻게 진행할까요?`
