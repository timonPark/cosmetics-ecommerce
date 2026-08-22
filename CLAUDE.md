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

## 폴더 구조

```
src/
  app/            # App Router 페이지 및 레이아웃
  components/     # 공통 컴포넌트
    ui/           # shadcn/ui 컴포넌트
  lib/            # 유틸리티, DB 클라이언트, 헬퍼
  db/             # Drizzle 스키마 및 마이그레이션
```

## 작업 프로세스 규칙

1. **마크다운 명세서는 330줄 제한**: 330줄이 넘어가면 파일을 분할한다.
2. **모든 작업은 이슈 → 브랜치 → PR 흐름을 따른다**:
   - GitHub에 이슈 생성
   - 해당 이슈 기반으로 브랜치 생성 (예: `feature/#1-product-list`)
   - 작업 완료 후 commit → push → PR 생성
   - PR 검토 후 main에 머지

## 코딩 규칙

- 컴포넌트: PascalCase (예: `ProductCard.tsx`)
- 파일/폴더: kebab-case (예: `product-list/`)
- 변수/함수: camelCase
- 서버 컴포넌트 우선, 클라이언트 컴포넌트는 `"use client"` 명시
- 이미지는 반드시 Next.js `<Image>` 컴포넌트 사용

## 커밋 메시지 규칙

```
feat: 새 기능
fix: 버그 수정
chore: 설정/도구 변경
docs: 문서 변경
refactor: 리팩토링
style: 스타일(UI) 변경
```

이슈 연결: 커밋/PR에 `closes #이슈번호` 표기 → 머지 시 이슈 자동 닫힘

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
