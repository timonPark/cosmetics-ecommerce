---
name: codex-review
description: "Codex(OpenAI)에게 현 브랜치 코드리뷰를 위임한다. Claude와 Codex 간 AI 교차 검증 목적. 사용자가 \"codex 리뷰\", \"codex로 리뷰해줘\", \"교차 검증\", \"/codex-review\" 등을 요청하면 사용한다."
allowed-tools:
  [
    'Bash(which:*)',
    'Bash(find:*)',
    'Bash(git branch:*)',
    'Bash(codex exec:*)',
    'Read(code-review/**)',
  ]
---

# Codex Review

Claude가 작성한 코드를 Codex(OpenAI)에게 리뷰 위임하여 AI 툴 간 교차 검증을 수행한다.
리뷰 결과는 Codex가 `/code-review` 스킬을 통해 `code-review/{브랜치명}/code-review.md`에 저장한다.

## 사용법

```
/codex-review
```

## 프로세스

1. **Codex 바이너리 경로 확인**
   - `which codex`로 PATH에서 먼저 탐색한다.
   - 없으면 `find "$HOME" -name "codex" -path "*/app-server-runtime/codex" 2>/dev/null | head -1`로 설치 경로를 찾는다.
   - 바이너리를 찾지 못하면 사용자에게 설치를 안내하고 종료한다.

2. **Codex 실행**
   - 찾은 경로로 아래 명령을 실행한다.
   ```bash
   {CODEX_PATH} exec "이 프로젝트에 /code-review 스킬을 사용해서 리뷰해주세요"
   ```
   - Codex는 프로젝트의 `.agents/skills/code-review/SKILL.md`를 읽고 스스로 리뷰를 수행한다.

3. **결과 안내**
   - 실행 완료 후 `code-review/{브랜치명}/code-review.md` 경로를 사용자에게 안내한다.
   - Codex 토큰 부족 등으로 중단된 경우 해당 사실을 사용자에게 전달한다.

## 목적

| 항목 | 내용 |
|---|---|
| 교차 검증 | Claude가 작성한 코드를 다른 AI(Codex)가 독립적으로 검토 |
| 편향 방지 | 동일 AI가 작성·검토할 때 발생하는 확증 편향 최소화 |
| 리뷰 저장 | Codex가 직접 `code-review/*.md` 파일로 결과 기록 |
