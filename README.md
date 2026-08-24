# 화장품 이커머스

특정 화장품 브랜드의 상품을 소개하는 이커머스 서비스. 상품 목록/상세 조회, 장바구니, 주문, 관리자 기능을 제공한다.

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프레임워크 | Next.js 15 (App Router) |
| UI | Tailwind CSS + shadcn/ui |
| ORM | Drizzle |
| DB / 인증 | Supabase (Postgres + Auth) |
| 이미지 저장 | Cloudflare R2 |
| 이미지 처리 | sharp (리사이즈 + WebP 변환) |
| 배포 | Vercel |

## 로컬 실행 방법

### 사전 요구사항

- Node.js 20+
- pnpm

### 1. 저장소 클론

```bash
git clone https://github.com/timonPark/cosmetics-ecommerce.git
cd cosmetics-ecommerce
```

### 2. 패키지 설치

```bash
pnpm install
```

### 3. 환경 변수 설정

프로젝트 루트에 `.env.local` 파일을 생성하고 아래 값을 채운다.

```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_DB_PASSWORD=
DATABASE_URL=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_ENDPOINT=
R2_PUBLIC_URL=
```

### 4. 개발 서버 실행

```bash
pnpm dev
```

[http://localhost:3000](http://localhost:3000) 에서 확인한다.

## 프로젝트 관리

- GitHub Project: [timonPark/projects/11](https://github.com/users/timonPark/projects/11)
