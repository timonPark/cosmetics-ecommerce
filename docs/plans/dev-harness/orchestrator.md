# 태스크 4: dev-harness 오케스트레이터

**산출물:** `.claude/commands/dev-harness.md`

---

## 오케스트레이터 동작 흐름

```
/dev-harness #이슈번호
  │
  ├── Step 1: gh issue view → 제목/라벨/본문 확인
  │
  ├── Step 2: {도메인}/{식별값} 패턴으로 에이전트 분류
  │           우선순위: 제목 → 라벨 → 본문 → AskUserQuestion
  │
  ├── Step 3: 작업 준비
  │           git checkout -b feature/#이슈번호-작업명 dev
  │           work_history/YYYY-MM-DD-{브랜치명}.md 생성
  │           GitHub Project Status → In Progress
  │
  ├── Step 4: 에이전트 실행
  │           Read .claude/agents/{에이전트}.md
  │           → Agent 툴 호출 금지, Claude가 단계별 직접 실행
  │
  └── Step 5: 완료 처리
              git push origin {브랜치명}
              gh pr create --base dev
              GitHub Project Status → Done
              work_history PR URL·머지 완료일(KST) 업데이트
```

## 분류 테이블

| 이슈 제목 패턴 | 에이전트 | 주요 스킬 체인 |
|---|---|---|
| `BE/feat` | be-feat | brainstorm → write-plan → be-dev → codex-review → tdd-be |
| `BE/fix` | be-fix | be-dev → codex-review → tdd-be |
| `BE/refactor` | be-refactor | brainstorm → be-dev → codex-review → tdd-be |
| `BE/perf` | be-perf | be-dev → codex-review → tdd-be |
| `FE/feat` | fe-feat | brainstorm → write-plan → fe-dev → codex-review → tdd-fe |
| `FE/fix` | fe-fix | fe-dev → codex-review → tdd-fe |
| `FE/style` | fe-style | fe-dev → codex-review |
| `FE/perf` | fe-perf | fe-dev → codex-review → tdd-fe |
| `공통/docs` | common-docs | 문서 작성 → codex-review |
| `공통/chore` | common-chore | 환경 설정 → codex-review |

## 핵심 제약

- **Agent 툴 호출 금지**: 에이전트 파일을 Read 후 Claude가 직접 실행
- **커밋 HARD GATE**: 모든 에이전트에서 사용자 명시적 승인 후에만 커밋
- **push**: `git push origin {브랜치명}` (명시적 브랜치명 필수)
- **`.claude/` 파일 수정**: docs/ 경유 cp 방식으로만 생성/수정
