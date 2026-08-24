# 태스크 3: 공통 에이전트 2개 + codex-review 스킬

---

## common-docs — 공통 문서 작업

**산출물:** `.claude/agents/common-docs.md`

Step 순서: 이슈 분석 → 문서 작성 → codex-review → 리뷰 반영 → 사용자 확인 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 이슈 분석 | 작성/수정할 문서 파악, 기존 문서 확인 |
| 문서 작성 | 330줄 제한 준수, `.claude/commands/` 는 docs/ 경유 cp 방식 |
| codex-review | 교차 검증 |
| 리뷰 반영 | 사실 오류·규칙 불일치 → 반드시 반영, 표현·구조 → 사용자 확인 |
| 사용자 확인 | 최종 내용 검토 요청 |
| 커밋 | `공통/docs: {내용} closes #이슈번호` |

---

## common-chore — 공통 환경 설정

**산출물:** `.claude/agents/common-chore.md`

Step 순서: 이슈 분석 → (brainstorm) → 환경 설정 → codex-review → 리뷰 반영 → 검증 → 커밋

| 단계 | 핵심 내용 |
|---|---|
| 이슈 분석 | 설정 변경 범위, 영향 파일/환경 확인 |
| brainstorm | 복잡한 환경 설정만 선택적 실행 |
| 환경 설정 | 패키지 설치, 설정 파일 수정, 단계별 커밋 |
| codex-review | 교차 검증 (보안 취약점·빌드 오류 포커스) |
| 리뷰 반영 | 보안·빌드 오류 → 반드시 반영, 설정값 제안 → 사용자 확인 |
| 검증 | `pnpm build` 또는 `pnpm dev` 실행 확인 |
| 커밋 | `공통/chore: {내용} closes #이슈번호` |

---

## codex-review 스킬

**산출물:**
- `.claude/commands/codex-review.md` — Claude가 Codex를 호출하는 스킬
- `.agents/skills/code-review/SKILL.md` — Codex가 읽고 실행하는 리뷰 스킬

### 동작 방식

```
Claude (codex-review 스킬 실행)
  → Codex CLI: codex exec "이 프로젝트에 /code-review 스킬을 사용해서 리뷰해주세요"
    → Codex가 .agents/skills/code-review/SKILL.md 읽고 리뷰 수행
      → code-review/{브랜치명}/code-review.md 저장
  → Claude가 결과 읽고 반영 여부 판단
```

### Codex 리뷰 관점 (이 프로젝트 특화)

- 레이어 규칙: Actions→Service→Repository 단방향, 레이어별 책임 준수
- 타입 안전성: 모든 파라미터·반환 타입 명시
- Drizzle 쿼리: N+1 여부, `returning()` 사용
- Supabase Auth: 인증 확인 위치 (입력 검증 직후)
- R2 업로드: DB 저장 전 수행 여부
- 테스트 커버리지: 변경 범위 대비 테스트 충분 여부
