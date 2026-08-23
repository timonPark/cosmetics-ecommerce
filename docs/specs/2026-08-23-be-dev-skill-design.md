# 백엔드 개발 스킬 설계

작성일: 2026-08-23

## 개요

Claude가 BE 코드(Actions/Service/Repository)를 작성할 때 따르는 행동 지침 스킬 문서.

---

## 스킬 메타데이터

| 항목 | 내용 |
|------|------|
| 파일 위치 | `.claude/commands/be-dev.md` |
| name | `be-dev` |
| description | BE 레이어(Actions/Service/Repository) 코드 작성 규칙. Server Action 패턴, Drizzle 쿼리, Supabase Auth 연동, R2 업로드 규칙. |
| allowed-tools | `Read`, `Write`, `Edit`, `Bash(npx tsc:*)`, `Bash(npx drizzle-kit:*)`, `mcp__ide__getDiagnostics` |

---

## 섹션 1 — BE 레이어 의사결정

코드 작성 전 반드시 레이어를 결정한다.

```
새 BE 코드 작성 시작
│
├── 외부에서 호출되는 진입점인가? (폼 처리, 버튼 클릭, 페이지 데이터 로딩)
│   └── Yes → Actions (src/actions/)
│       - 입력 검증
│       - 인증 확인 (필요 시)
│       - Service 호출
│       - ActionResult 반환
│
├── 비즈니스 로직인가? (조건 판단, 계산, 외부 서비스 호출)
│   └── Yes → Service (src/services/{도메인}/)
│       - Repository 호출로 데이터 조회/저장
│       - R2 업로드, sharp 처리 등 외부 서비스 직접 호출 가능
│       - 유효하지 않은 상태면 AppError throw
│
├── DB 쿼리인가? (조회, 삽입, 수정, 삭제)
│   └── Yes → Repository (src/repositories/{도메인}/)
│       - Drizzle 쿼리만 작성
│       - 비즈니스 로직 금지
│
└── 테이블/컬럼 정의인가?
    └── Yes → DB (src/db/schema.ts)
```

**핵심 규칙**

- 레이어 간 호출은 Actions → Service → Repository 단방향만 허용. 역방향·건너뛰기 금지
- Actions에서 DB 직접 접근 금지
- Repository에서 비즈니스 로직 작성 금지

---

## 섹션 2 — 공통 타입 패턴

BE 전체에서 공유하는 에러·결과 타입. `src/types/` 에 정의한다.

### 2-1. ErrorCode enum

```typescript
// src/types/error-code.enum.ts
export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  CONFLICT = 'CONFLICT',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
}
```

### 2-2. AppError 클래스

```typescript
// src/types/app-error.ts
import { ErrorCode } from '@/types/error-code.enum'

export class AppError extends Error {
  code: ErrorCode

  constructor(code: ErrorCode, message: string) {
    super(message)
    this.code = code
    this.name = 'AppError'
  }
}
```

### 2-3. ActionResult 타입

```typescript
// src/types/action.ts
export type ActionResult<T> =
  | { success: true; data: T }
  | { success: false; error: string; code: string }
```

**에러 흐름 요약**

```
Repository → null 반환
Service    → AppError throw (NOT_FOUND, VALIDATION_ERROR 등)
Actions    → try/catch로 AppError 잡아서 ActionResult 반환
FE Hook    → result.success 분기로 처리
```

---

## 섹션 3 — 레이어별 코드 패턴

### 3-1. Actions (Server Action)

```typescript
// src/actions/product.actions.ts
'use server'

import { ProductService } from '@/services/product/product.service'
import { AppError } from '@/types/app-error'
import type { ActionResult } from '@/types/action'
import type { Product } from '@/types/product'

type GetProductInput = {
  id: number
}

export const getProduct = async (input: GetProductInput): Promise<ActionResult<Product>> => {
  if (!input.id || input.id <= 0) {
    return { success: false, error: '유효하지 않은 상품 ID입니다', code: 'VALIDATION_ERROR' }
  }

  try {
    const product: Product = await ProductService.findById(input.id)
    return { success: true, data: product }
  } catch (e: unknown) {
    if (e instanceof AppError) {
      return { success: false, error: e.message, code: e.code }
    }
    return { success: false, error: '서버 오류가 발생했습니다', code: 'INTERNAL_ERROR' }
  }
}
```

**규칙**:
- 파일 최상단 `'use server'` 필수
- 화살표 함수
- 입력 검증 → (인증 확인) → Service 호출 순서 고정
- DB·비즈니스 로직 직접 작성 금지 — Service 호출만

---

### 3-2. Service

```typescript
// src/services/product/product.service.ts
import { ProductRepository } from '@/repositories/product/product.repository'
import { AppError } from '@/types/app-error'
import { ErrorCode } from '@/types/error-code.enum'
import type { Product } from '@/types/product'

export const ProductService = {
  findById: async (id: number): Promise<Product> => {
    const product: Product | null = await ProductRepository.findById(id)
    if (!product) {
      throw new AppError(ErrorCode.NOT_FOUND, '상품을 찾을 수 없습니다')
    }
    return product
  },

  findAll: async (): Promise<Product[]> => {
    return ProductRepository.findAll()
  },
}
```

**규칙**:
- `export const ServiceName = { method: async (...) => ... }` 형태
- Repository만 호출. DB 직접 접근 금지
- 데이터가 없으면 `AppError` throw (null 반환 금지)
- R2·sharp 등 외부 서비스 직접 호출 가능

---

### 3-3. Repository

```typescript
// src/repositories/product/product.repository.ts
import { eq, desc, and } from 'drizzle-orm'
import { db } from '@/db'
import { products } from '@/db/schema'
import type { Product } from '@/types/product'

export const ProductRepository = {
  findById: async (id: number): Promise<Product | null> => {
    const result: Product[] = await db
      .select()
      .from(products)
      .where(eq(products.id, id))
      .limit(1)
    return result[0] ?? null
  },

  findAll: async (): Promise<Product[]> => {
    return db
      .select()
      .from(products)
      .where(eq(products.isActive, true))
      .orderBy(desc(products.createdAt))
  },

  create: async (data: Omit<Product, 'id' | 'createdAt' | 'updatedAt'>): Promise<Product> => {
    const result: Product[] = await db
      .insert(products)
      .values(data)
      .returning()
    return result[0]
  },

  update: async (id: number, data: Partial<Omit<Product, 'id' | 'createdAt'>>): Promise<Product | null> => {
    const result: Product[] = await db
      .update(products)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(products.id, id))
      .returning()
    return result[0] ?? null
  },

  delete: async (id: number): Promise<void> => {
    await db.delete(products).where(eq(products.id, id))
  },
}
```

**규칙**:
- `export const RepositoryName = { method: async (...) => ... }` 형태
- 존재하지 않으면 `null` 반환 (throw 금지 — Service가 처리)
- 비즈니스 로직 금지 — Drizzle 쿼리만 작성
- `returning()`으로 insert/update 결과 반환

---

## 섹션 4 — Supabase Auth 연동

인증이 필요한 Action에서만 사용한다.

### 4-1. 서버 클라이언트 생성

```typescript
// src/lib/supabase.ts (서버 전용)
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export const createSupabaseServerClient = async () => {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        },
      },
    }
  )
}
```

### 4-2. Actions에서 인증 확인

```typescript
// src/actions/order.actions.ts
'use server'

import { createSupabaseServerClient } from '@/lib/supabase'
import { OrderService } from '@/services/order/order.service'
import { AppError } from '@/types/app-error'
import type { ActionResult } from '@/types/action'
import type { Order } from '@/types/order'

export const createOrder = async (input: CreateOrderInput): Promise<ActionResult<Order>> => {
  const supabase = await createSupabaseServerClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return { success: false, error: '로그인이 필요합니다', code: 'UNAUTHORIZED' }
  }

  try {
    const order: Order = await OrderService.create({ ...input, userId: user.id })
    return { success: true, data: order }
  } catch (e: unknown) {
    if (e instanceof AppError) {
      return { success: false, error: e.message, code: e.code }
    }
    return { success: false, error: '서버 오류가 발생했습니다', code: 'INTERNAL_ERROR' }
  }
}
```

**규칙**:
- 인증 확인은 입력 검증 바로 다음, Service 호출 전
- 비인증 시 즉시 `UNAUTHORIZED` 반환
- `user.id`를 Service에 전달 — Service는 userId를 신뢰(Actions에서 검증 완료)

---

## 섹션 5 — R2 이미지 업로드 연동

Service 레이어에서 `src/lib/r2.ts` 함수를 직접 호출한다.

```typescript
// src/services/product/product.service.ts (이미지 업로드 포함 버전)
import { ProductRepository } from '@/repositories/product/product.repository'
import { uploadThumbnail, uploadDetailImage } from '@/lib/r2'
import { AppError } from '@/types/app-error'
import { ErrorCode } from '@/types/error-code.enum'
import type { Product } from '@/types/product'

type CreateProductInput = {
  name: string
  slug: string
  price: number
  thumbnailBuffer: Buffer
  detailImageBuffer: Buffer
}

export const ProductService = {
  create: async (input: CreateProductInput): Promise<Product> => {
    const [thumbnailUrl, detailImageUrl]: [string, string] = await Promise.all([
      uploadThumbnail(input.slug, input.thumbnailBuffer),
      uploadDetailImage(input.slug, input.detailImageBuffer),
    ])

    return ProductRepository.create({
      name: input.name,
      slug: input.slug,
      price: input.price,
      thumbnailUrl,
      detailImageUrl,
      isActive: true,
    })
  },
}
```

**규칙**:
- R2·sharp 호출은 Service에서만
- 이미지 업로드는 DB 저장 전에 수행 (업로드 실패 시 DB 저장 안 됨)
- Actions에서 `FormData`의 파일을 `Buffer`로 변환 후 Service에 전달

### Actions에서 파일 → Buffer 변환

```typescript
// Actions에서 FormData 처리
export const uploadProductImages = async (formData: FormData): Promise<ActionResult<Product>> => {
  const thumbnailFile = formData.get('thumbnail') as File | null
  const detailFile = formData.get('detailImage') as File | null

  if (!thumbnailFile || !detailFile) {
    return { success: false, error: '이미지 파일이 필요합니다', code: 'VALIDATION_ERROR' }
  }

  const [thumbnailBuffer, detailImageBuffer]: [Buffer, Buffer] = await Promise.all([
    Buffer.from(await thumbnailFile.arrayBuffer()),
    Buffer.from(await detailFile.arrayBuffer()),
  ])

  // Service에 Buffer 전달
  ...
}
```

---

## 섹션 6 — Drizzle 스키마 변경 절차

스키마(`src/db/schema.ts`) 수정 시 반드시 마이그레이션을 실행한다.

```bash
# 1. 스키마 변경 후 마이그레이션 파일 생성
npx drizzle-kit generate

# 2. 개발 DB에 적용 (로컬)
npx drizzle-kit push

# 3. 프로덕션 반영은 배포 시 별도 마이그레이션 실행
```

**규칙**:
- 스키마 변경 → 마이그레이션 생성 → DB 적용 순서 반드시 준수
- `drizzle-kit push`는 개발/테스트 환경에서만. 프로덕션은 `drizzle-kit migrate`
- 마이그레이션 파일(`src/db/migrations/`)은 git에 커밋

---

## 섹션 7 — import 순서

```typescript
// 1. Next.js 서버 유틸
import { cookies } from 'next/headers'

// 2. 외부 라이브러리
import { eq, desc } from 'drizzle-orm'

// 3. 내부 모듈 — 절대 경로 (@/)
import { db } from '@/db'
import { products } from '@/db/schema'
import { ProductService } from '@/services/product/product.service'
import { AppError } from '@/types/app-error'
import type { Product } from '@/types/product'
import type { ActionResult } from '@/types/action'
```

그룹 사이 빈 줄 하나. `import type`으로 타입 import 분리.

---

## 섹션 8 — 체크리스트

### Actions

- [ ] 파일 최상단에 `'use server'`가 있는가
- [ ] 모든 함수가 화살표 함수인가
- [ ] 입력 검증 → 인증 확인(필요 시) → Service 호출 순서인가
- [ ] `ActionResult<T>` 반환 타입이 명시되어 있는가
- [ ] `try/catch`로 `AppError`를 잡아 `ActionResult`로 변환하는가
- [ ] DB 직접 접근이 없는가

### Service

- [ ] `export const ServiceName = { ... }` 형태인가
- [ ] 모든 메서드가 화살표 함수인가
- [ ] 데이터 없음을 `AppError` throw로 처리하는가 (null 반환 금지)
- [ ] Repository만 호출하는가 (DB 직접 접근 금지)
- [ ] 모든 파라미터·반환 타입에 TypeScript 타입이 명시되어 있는가

### Repository

- [ ] `export const RepositoryName = { ... }` 형태인가
- [ ] 데이터 없음을 `null` 반환으로 처리하는가 (throw 금지)
- [ ] Drizzle 쿼리만 작성되어 있는가 (비즈니스 로직 없음)
- [ ] `returning()`으로 insert/update 결과를 반환하는가
- [ ] 모든 파라미터·반환 타입에 TypeScript 타입이 명시되어 있는가

### 공통

- [ ] import 순서 규칙을 따르는가
- [ ] `npx tsc --noEmit` 통과하는가
- [ ] 스키마 변경 시 `npx drizzle-kit generate` & `push`를 실행했는가

---

## TDD 연동

BE 코드 작성 후 테스트 작성은 `/tdd-be` 스킬을 사용한다.

- Service 단위 테스트: `__tests__/unit/services/{도메인}/{파일명}.service.test.ts`
- Repository 통합 테스트: `__tests__/integration/repositories/{도메인}/{파일명}.repository.test.ts`

---

## 범위 외

- FE 레이어(Page/Component/Hook) 작성 → `/fe-dev` 스킬
- GitHub 이슈·브랜치 관리 → `/github-project` 스킬
- TDD 작성 → `/tdd-be` 스킬
