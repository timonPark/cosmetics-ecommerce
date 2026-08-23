@AGENTS.md

# 화장품 이커머스 프로젝트

## 프로젝트 개요

화장품 브랜드 이커머스 사이트. 상품 약 100개, 상품당 썸네일 + 상세이미지 운영.
바이브코딩(AI 코딩 도구)으로 빠르게 개발하고 Vercel에 배포.

## 기술 스택

| 영역 | 선택 |
|---|---|
| 프레임워크 | Next.js 15 (App Router) |
| UI | Tailwind CSS + shadcn/ui |
| ORM | Drizzle |
| DB / 인증 | Supabase (Postgres + Auth) |
| 이미지 저장 | Cloudflare R2 |
| 이미지 처리 | sharp (리사이즈 + WebP 변환) |
| 배포 | Vercel |

## 폴더 구조 및 레이어

@docs/folder-structure.md

## 작업 프로세스 규칙

1. **마크다운 명세서는 330줄 제한**: 330줄이 넘어가면 `@파일경로` 방식으로 분리한다.

2. **브랜치 전략**:
   ```
   main                           # 프로덕션 배포 브랜치 (직접 커밋 금지)
   └── dev                        # 기본 브랜치, 개발 통합
       ├── feature/#이슈번호-작업명  # 기능 개발 브랜치
       └── hotfix/#이슈번호-작업명   # 프로덕션 긴급 수정 브랜치 (main 기반)
   ```
   - `feature/` 브랜치: 모든 일반 작업 (feat, fix, refactor, docs, chore, perf)
   - `hotfix/` 브랜치: 프로덕션(main) 긴급 수정 시에만 사용. main 기반으로 생성 후 main·dev 양쪽에 머지
   - 브랜치명 예시: `feature/#15-product-service`, `hotfix/#22-image-upload-fix`

3. **작업 흐름 (모든 작업에 적용)**:
   - GitHub에 이슈 생성
   - `dev` 기반으로 feature 브랜치 생성: `git checkout -b feature/#이슈번호-작업명 dev`
   - **브랜치 생성 즉시** `work_history/YYYY-MM-DD-{브랜치명}.md` 파일 생성 후 작업 내용 기록 시작
   - 작업 완료 후 commit → push
   - `dev` ← feature 브랜치로 PR 생성 + `closes #이슈번호` 표기
   - PR 검토 후 dev에 머지
   - 머지 완료 후 해당 `work_history` 파일에 PR URL 및 머지 완료일 업데이트
   - 배포 시 `main` ← `dev` PR 생성 후 머지

4. **work_history 규칙**:
   - 위치: 프로젝트 루트 `work_history/` 폴더 (`.gitignore` 처리 — 로컬 전용)
   - 파일명: `YYYY-MM-DD-{브랜치명}.md`
   - 모든 작업(이슈, 브랜치, 코드 변경, 결정 사항)을 빠짐없이 기록
   - **파일 구조 및 작성 방법은 반드시 아래 스펙을 참고할 것**

@docs/work-history-spec.md

## 코딩 규칙 및 스타일

@docs/coding-standards.md

## 환경 변수

`.env.local` 파일에 설정 (`.env*`는 gitignore에 포함되어 있음):

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=
```
