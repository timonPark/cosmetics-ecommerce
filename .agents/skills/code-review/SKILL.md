---
description: '현 브랜치에서 변경된 내용을 코드 리뷰하고, 프로젝트 루트의 code-review/{브랜치명}/code-review.md 파일로 리뷰 결과를 저장합니다.'
allowed-tools:
  [
    'Bash(git branch:*)',
    'Bash(git status:*)',
    'Bash(git diff:*)',
    'Bash(git log:*)',
    'Bash(mkdir:*)',
    'Write(code-review/**)',
    'Edit(code-review/**)',
  ]
---

# Code Review

현 브랜치에서 변경된 내용을 기준으로 코드 리뷰를 수행하고, 리뷰 결과를 프로젝트 루트의 `code-review/{브랜치명}/code-review.md`에 저장한다.

## 트리거

사용자가 다음과 같이 요청하면 이 skill을 사용한다.

- `코드리뷰`
- `리뷰해줘`
- `변경사항 리뷰`
- `code-review`
- `/code-review`
- `review`

## 프로세스

1. **현재 브랜치 확인**
   - `git branch --show-current`로 현재 브랜치명을 확인한다.
   - 브랜치명에 `/`나 `#`이 포함되면 파일 시스템에서 단일 폴더로 다루기 위해 `/`를 `__`, `#`를 `-`로 치환한다.
   - 원본 브랜치명은 리뷰 문서에 반드시 기록한다.

2. **변경사항 수집**
   - `git status --short`로 변경 파일 목록을 확인한다.
   - `git diff --stat`으로 변경 규모를 파악한다.
   - `git diff`로 unstaged 변경사항을 검토한다.
   - `git diff --cached`로 staged 변경사항을 검토한다.
   - 필요하면 `git log --oneline --decorate -n 10`으로 최근 커밋 맥락을 확인한다.

3. **프로젝트 규칙 확인**
   - `docs/coding-standards.md`를 확인한다.
   - `docs/folder-structure.md`를 확인한다.

4. **리뷰 관점**

   **레이어 규칙 (최우선)**
   - Actions(`src/actions/`): `'use server'` 명시, 화살표 함수, 입력 검증 → Service 호출 순서, DB 직접 접근 금지
   - Service(`src/services/`): Repository만 호출, 데이터 없음 시 AppError throw (null 반환 금지)
   - Repository(`src/repositories/`): Drizzle 쿼리만 작성, 비즈니스 로직 금지, 데이터 없음 시 null 반환
   - Component(`src/components/`): 비즈니스 로직·상태·사이드이펙트 금지, Hook 호출만 허용
   - Hook(`src/hooks/`): `"use client"` 환경 전용, Server Actions 호출은 Hook에서만

   **타입 안전성**
   - 모든 변수·함수 파라미터·반환 타입에 TypeScript 타입 명시 (추론 의존 금지)
   - `ActionResult<T>` 반환 타입 올바른 사용 여부

   **보안 및 데이터**
   - 인증 없이 민감 데이터에 접근하는 경우 확인
   - Supabase Auth 인증 확인 위치 (입력 검증 직후, Service 호출 전)
   - 환경변수 하드코딩 여부

   **쿼리 및 성능**
   - Drizzle 쿼리 조건, N+1성 접근 여부
   - `returning()`으로 insert/update 결과 반환 여부
   - R2 업로드: DB 저장 전 수행 여부

   **코드 스타일**
   - 컴포넌트는 함수 선언식, 그 외는 화살표 함수
   - named export만 사용 (default export 금지)
   - import 순서: Next.js → 외부 라이브러리 → 내부 모듈(@/) → 상대 경로

   **테스트**
   - 변경 범위에 맞는 테스트 추가 여부
   - Service 단위 테스트: `__tests__/unit/services/`
   - Repository 통합 테스트: `__tests__/integration/repositories/`
   - FE 테스트: 소스 파일 옆 코로케이션

5. **리뷰 문서 저장**
   - 프로젝트 루트에 `code-review/{브랜치명}/` 폴더를 만든다.
   - 리뷰 결과를 `code-review/{브랜치명}/code-review.md`에 저장한다.

## 리뷰 문서 템플릿

```markdown
# Code Review: {원본 브랜치명}

## 메타
- 리뷰 일시: YYYY-MM-DD HH:mm (KST)
- 브랜치: `{원본 브랜치명}`
- 리뷰 대상: 현 브랜치의 staged/unstaged 변경사항

## 변경 요약
- 변경 목적:
- 주요 변경 파일:
- 영향 범위:

## 코드 리뷰 요약

| # | 심각도 | 파일 | 라인 | 항목 | 상태 |
|---|--------|------|------|------|------|

**종합**:

## 코드 리뷰 상세

### Critical
- 없음

### Major
- 없음

### Minor
- 없음

## 상세 코멘트

### `{파일 경로}`
- 이슈:
- 근거:
- 제안:

## 테스트 관점
- 확인된 테스트:
- 추가 권장 테스트:

## 최종 판단
- 병합 가능 여부:
- 남은 리스크:
```

## 작성 규칙

- 문제를 발견하면 심각도 순서로 작성한다: `Critical` → `Major` → `Minor`.
- 각 코멘트는 파일 경로, 문제, 근거, 제안을 포함한다.
- 확실하지 않은 내용은 단정하지 말고 `확인 필요`로 표시한다.
- 문제가 없으면 `특이사항 없음` 또는 `없음`으로 명확히 적는다.
- 코드 리뷰 문서에는 AI, Claude, Codex 등 작성 주체를 언급하지 않는다.
