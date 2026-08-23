# 폴더 구조

```
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── (shop)/                 # [FE] 쇼핑몰 라우트 그룹
│   │   │   ├── products/           # [FE] 상품 목록/상세 페이지
│   │   │   ├── cart/               # [FE] 장바구니 페이지
│   │   │   └── orders/             # [FE] 주문 페이지
│   │   ├── (admin)/                # [FE] 관리자 라우트 그룹
│   │   │   ├── products/           # [FE] 상품 관리 페이지
│   │   │   └── orders/             # [FE] 주문 관리 페이지
│   │   ├── api/                    # [BE] API Routes (외부 웹훅·OAuth 콜백 전용)
│   │   ├── layout.tsx              # [FE] 루트 레이아웃
│   │   └── globals.css             # [FE] 전역 스타일
│   ├── components/                 # [FE] UI 컴포넌트 (렌더링 전용, 비즈니스 로직 금지)
│   │   ├── ui/                     # [FE] shadcn/ui 자동 생성 — 직접 수정 금지
│   │   ├── product/                # [FE] 상품 관련 컴포넌트
│   │   │   ├── ProductCard.tsx
│   │   │   └── ProductCard.test.tsx  # [FE] 코로케이션 테스트
│   │   ├── cart/                   # [FE] 장바구니 컴포넌트
│   │   └── layout/                 # [FE] 헤더, 푸터 등 레이아웃 컴포넌트
│   ├── hooks/                      # [FE] 커스텀 React Hooks ("use client" 전용)
│   │   └── useCart.ts              # [FE] 예) useCart.test.ts 코로케이션
│   ├── actions/                    # [BE] Controller — 입력 검증, 인증 확인, Service 호출
│   │   └── product.actions.ts
│   ├── services/                   # [BE] Service — 비즈니스 로직
│   │   └── product.service.ts
│   ├── repositories/               # [BE] Repository — DB 쿼리 전담
│   │   └── product.repository.ts
│   ├── db/                         # [BE] Drizzle ORM
│   │   ├── schema.ts               # [BE] 테이블 스키마 정의
│   │   ├── index.ts                # [BE] DB 클라이언트
│   │   └── migrations/             # [BE] Drizzle 마이그레이션 파일
│   ├── lib/                        # [BE] 서버 전용 유틸리티 및 외부 서비스 클라이언트
│   │   ├── supabase.ts             # [BE] Supabase 클라이언트
│   │   ├── r2.ts                   # [BE] Cloudflare R2 업로드
│   │   ├── image.ts                # [BE] sharp 이미지 처리
│   │   └── utils.ts                # [BE/FE] 공통 유틸리티 (순수 함수만)
│   └── types/                      # [BE/FE] 공통 TypeScript 타입 정의
├── __tests__/                      # [BE] 테스트 파일
│   ├── unit/                       # 단위 테스트 — Repository mock 사용
│   │   └── services/               # Service 레이어 테스트
│   └── integration/                # 통합 테스트 — 테스트 DB 연결
│       └── repositories/           # Repository 레이어 테스트
├── docs/                           # 프로젝트 문서
│   ├── specs/                      # 기능 설계 문서 (/brainstorm 산출물)
│   ├── plans/                      # 구현 계획 문서 (/write-plan 산출물)
│   └── work-history-spec.md        # work_history 파일 규격
├── public/                         # [FE] 정적 에셋
└── work_history/                   # 로컬 작업 기록 (gitignore)
```

## FE 레이어 구조 (3-Layer)

```
Page → Component → Hook → Server Actions (BE)
```

| 레이어 | 경로 | 책임 | 테스트 | 규칙 |
|--------|------|------|--------|------|
| **Page** | `src/app/` | 라우팅, 레이아웃, 서버 컴포넌트 데이터 패칭 | 없음 | 서버 컴포넌트 기본. 데이터를 props로 Component에 전달 |
| **Component** | `src/components/` | UI 렌더링 전담 | **단위 테스트** (코로케이션) | 비즈니스 로직·상태·사이드이펙트 금지. Hook 호출만 허용 |
| **Hook** | `src/hooks/` | 클라이언트 상태·사이드이펙트 캡슐화 | **단위 테스트** (코로케이션) | Server Actions 호출은 Hook에서만. `"use client"` 환경 전용 |

## BE 레이어 구조 (4-Layer)

```
Actions (Controller) → Service → Repository → DB
```

| 레이어 | 경로 | 책임 | 테스트 | 규칙 |
|--------|------|------|--------|------|
| **Actions** | `src/actions/` | 입력 검증, 인증 확인, Service 호출, 응답 반환 | 없음 | `"use server"` 명시. DB·비즈니스 로직 직접 작성 금지 |
| **Service** | `src/services/` | 비즈니스 로직 | **단위 테스트** (Repository mock) | Repository만 호출. 외부 서비스(R2·sharp 등) 호출 가능 |
| **Repository** | `src/repositories/` | DB 쿼리 전담 | **통합 테스트** (테스트 DB 연결) | Drizzle 쿼리만 작성. 비즈니스 로직 금지 |
| **DB** | `src/db/` | 스키마 정의, DB 클라이언트 | 없음 | 스키마·마이그레이션 외 로직 없음 |

## 영역 구분 원칙

| 구분 | 영역 | 핵심 규칙 |
|------|------|-----------|
| **[FE]** | `app/(shop)/`, `app/(admin)/`, `components/`, `hooks/` | `"use client"` 필요 시에만 명시. 비즈니스 로직 작성 금지 — `actions/` 호출만 |
| **[BE]** | `actions/`, `services/`, `repositories/`, `db/`, `lib/` (utils 제외), `app/api/` | 서버에서만 실행. `"use server"` 명시. 클라이언트 import 금지 |
| **[BE/FE]** | `types/`, `lib/utils.ts` | 순수 함수·타입만 허용. 외부 서비스·DB 접근 금지 |

## 배치 원칙

- **Server Component 우선**: `app/` 내 컴포넌트는 기본 서버 컴포넌트. 클라이언트 상태가 필요한 경우에만 `"use client"` 추가
- **Server Actions 우선**: DB 접근·폼 처리는 `actions/` 에 위치. `app/api/` 는 외부 웹훅·OAuth 콜백에만 사용
- **레이어 간 단방향 호출**: Actions → Service → Repository 방향만 허용. 역방향·건너뛰기 금지
- **컴포넌트는 렌더링만**: 상태·사이드이펙트·Server Actions 호출은 모두 Hook으로 분리
- **FE 테스트 — 코로케이션**: 컴포넌트·훅 테스트는 소스 파일 옆에 위치. `ProductCard.tsx` → `ProductCard.test.tsx`
- **BE 테스트 — 미러링**: BE 테스트는 `__tests__/` 에 미러링
  - Service 단위 테스트: `src/services/product.service.ts` → `__tests__/unit/services/product.service.test.ts`
  - Repository 통합 테스트: `src/repositories/product.repository.ts` → `__tests__/integration/repositories/product.repository.test.ts`
- **shadcn/ui 래퍼**: `src/components/ui/` 는 CLI 자동 생성. 커스터마이징이 필요하면 래퍼 컴포넌트를 만든다
