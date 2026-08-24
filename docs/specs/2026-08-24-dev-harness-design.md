# dev-harness 스킬 설계 문서

**목표**: GitHub 이슈 번호를 입력받아 작업 유형을 분류하고, 해당 에이전트 스펙을 Read해 Claude가 직접 단계별로 실행하는 개발 워크플로우 오케스트레이터

**참고**: cdp-server의 work-manager 스킬 컨셉을 이 프로젝트에 맞게 재설계

---

## 파일 구조

```
.claude/
├── commands/
│   └── dev-harness.md        # 오케스트레이터 스킬
└── agents/
    ├── be-feat.md            # BE 신규 기능
    ├── be-fix.md             # BE 버그 수정
    ├── be-refactor.md        # BE 리팩토링
    ├── be-perf.md            # BE 성능 개선
    ├── fe-feat.md            # FE 화면 기능 개발
    ├── fe-fix.md             # FE 버그 수정
    ├── fe-style.md           # FE 디자인/스타일 변경
    ├── fe-perf.md            # FE 성능 개선
    ├── common-docs.md        # 공통 문서 작업
    └── common-chore.md       # 공통 환경 설정
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
- 각 단계 시작 시 진행 상태 표 출력:

```
| 단계 | 상태 |
|---|---|
| Step 1 — 이슈 분석 | ✅ 완료 |
| Step 2 — brainstorm | ▶ 진행 중 |
| Step 3 — write-plan | ⬜ 대기 |
...
```

**Step 5 — 완료 처리**
- `git push origin {브랜치명}` 후 PR 생성
- GitHub Project Status → `Done`
- work_history PR URL·머지 완료일 업데이트

---

## 에이전트 스펙

### be-feat.md — BE 신규 기능

```
Step 1 — 이슈 분석
  - 이슈 본문 확인, 관련 레이어(Actions/Service/Repository) 파악
  - 기존 유사 코드 탐색

Step 2 — brainstorm 스킬 실행
  - /brainstorm으로 설계 브레인스토밍 진행
  - 스펙 문서 작성 및 커밋

Step 3 — write-plan 스킬 실행
  - /write-plan으로 구현 계획 작성
  - 계획 문서 커밋

Step 4 — be-dev 스킬 실행
  - be-dev 스킬 가이드에 따라 Actions/Service/Repository 구현
  - 각 레이어 완료 시 커밋

Step 5 — tdd-be 스킬 실행
  - Service 단위 테스트 작성
  - Repository 통합 테스트 작성
  - 테스트 통과 확인

Step 6 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인

Step 7 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### be-fix.md — BE 버그 수정

```
Step 1 — 버그 재현 및 진단
  - 이슈 본문에서 재현 조건 파악
  - 관련 코드(Actions/Service/Repository) 탐색
  - 원인 특정 후 사용자에게 진단 결과 보고

Step 2 — be-dev 스킬 실행
  - 수정 범위를 최소화해 해당 레이어만 수정
  - 수정 완료 후 커밋

Step 3 — tdd-be 스킬 실행
  - 버그 재현하는 실패 테스트 먼저 작성
  - 수정 후 테스트 통과 확인

Step 4 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인

Step 5 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### be-refactor.md — BE 리팩토링

```
Step 1 — 이슈 분석
  - 리팩토링 대상 코드 탐색
  - 현재 구조의 문제점 파악

Step 2 — brainstorm 스킬 실행
  - 리팩토링 방향 설계
  - 동작 변경 없음을 보장할 전략 수립

Step 3 — be-dev 스킬 실행
  - 레이어 구조 개선 구현
  - 단계별 커밋 (기능 변경 없이 구조만 변경)

Step 4 — tdd-be 스킬 실행
  - 기존 테스트 통과 확인
  - 필요시 테스트 보강

Step 5 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인 (리팩토링 전과 동일한 결과)

Step 6 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### be-perf.md — BE 성능 개선

```
Step 1 — 성능 측정 및 분석
  - 병목 지점 파악 (쿼리, 이미지 처리 등)
  - 현재 성능 지표 기록

Step 2 — be-dev 스킬 실행
  - 쿼리 최적화 또는 이미지 처리 성능 개선 구현
  - 단계별 커밋

Step 3 — tdd-be 스킬 실행
  - 기존 동작 보장 테스트 확인

Step 4 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인
  - 성능 개선 결과 사용자에게 보고

Step 5 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### fe-feat.md — FE 화면 기능 개발

```
Step 1 — 이슈 분석
  - 이슈 본문 확인, Figma 디자인 링크 확인
  - 관련 레이어(Page/Component/Hook) 파악

Step 2 — brainstorm 스킬 실행
  - /brainstorm으로 컴포넌트 구조 설계
  - 스펙 문서 작성 및 커밋

Step 3 — write-plan 스킬 실행
  - /write-plan으로 구현 계획 작성
  - 계획 문서 커밋

Step 4 — fe-dev 스킬 실행
  - fe-dev 스킬 가이드에 따라 Page/Component/Hook 구현
  - 각 단위 완료 시 커밋

Step 5 — tdd-fe 스킬 실행
  - Component 단위 테스트 작성
  - Hook 단위 테스트 작성
  - 테스트 통과 확인

Step 6 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인

Step 7 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### fe-fix.md — FE 버그 수정

```
Step 1 — 버그 재현 및 진단
  - 이슈 본문에서 재현 조건 파악
  - 관련 Component/Hook 탐색
  - 원인 특정 후 사용자에게 진단 결과 보고

Step 2 — fe-dev 스킬 실행
  - 수정 범위 최소화, 해당 레이어만 수정
  - 수정 완료 후 커밋

Step 3 — tdd-fe 스킬 실행
  - 버그 재현하는 실패 테스트 먼저 작성
  - 수정 후 테스트 통과 확인

Step 4 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인

Step 5 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### fe-style.md — FE 디자인/스타일 변경

```
Step 1 — 이슈 분석
  - Figma 디자인 링크 확인 (있는 경우)
  - 변경 대상 Component 파악

Step 2 — fe-dev 스킬 실행
  - Tailwind CSS / shadcn/ui 기반 스타일 변경 구현
  - 단계별 커밋

Step 3 — 검증
  - npx tsc --noEmit 통과 확인
  - 시각적 결과 사용자 확인 요청

Step 4 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### fe-perf.md — FE 성능 개선

```
Step 1 — 성능 측정 및 분석
  - 렌더링 병목 또는 번들 크기 문제 파악
  - 현재 상태 기록

Step 2 — fe-dev 스킬 실행
  - 렌더링 최적화 또는 번들 최적화 구현
  - 단계별 커밋

Step 3 — tdd-fe 스킬 실행
  - 기존 동작 보장 테스트 확인

Step 4 — 검증
  - npx tsc --noEmit 통과 확인
  - pnpm test 통과 확인
  - 성능 개선 결과 사용자에게 보고

Step 5 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### common-docs.md — 공통 문서 작업

```
Step 1 — 이슈 분석
  - 작성/수정할 문서 파악
  - 관련 기존 문서 확인

Step 2 — 문서 작성
  - 이슈 요구사항에 맞게 문서 작성 또는 수정
  - CLAUDE.md 330줄 제한 준수 (초과 시 @파일 분리)

Step 3 — 사용자 확인
  - 작성된 내용 사용자에게 검토 요청

Step 4 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

### common-chore.md — 공통 환경 설정

```
Step 1 — 이슈 분석
  - 설정 변경 범위 파악
  - 영향 받는 파일/환경 확인

Step 2 — (필요시) brainstorm 스킬 실행
  - 복잡한 환경 설정의 경우 brainstorm으로 접근법 먼저 설계

Step 3 — 환경 설정 작업
  - 패키지 설치, 설정 파일 수정 등
  - 단계별 커밋

Step 4 — 검증
  - 설정 적용 확인 (빌드/실행 테스트)

Step 5 — 커밋
  - 사용자 명시적 승인 후 커밋
```

---

## 투명성 원칙

dev-harness 및 모든 에이전트는 아래 형식으로 진행 상황을 출력한다.

- 단계 시작: `▶ [단계명] {하려는 작업 한 줄 설명}`
- 단계 완료: `✅ [단계명] {완료 결과 한 줄 요약}`
- 병목 발생: `🚧 [병목] {상황 설명} — 어떻게 진행할까요?`
