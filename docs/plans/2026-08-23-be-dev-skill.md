# 백엔드 개발 스킬 구현 계획

**목표:** Claude가 BE 코드(Actions/Service/Repository) 작성 시 따르는 행동 지침 스킬 파일을 작성한다.

**아키텍처:** `.claude/commands/be-dev.md` 단일 파일. 기존 스킬 파일(fe-dev.md, tdd-be.md)과 동일한 YAML frontmatter + 마크다운 구조를 따른다. 레이어 의사결정 트리 → 공통 타입 → 레이어별 코드 패턴 → Auth/R2/Drizzle 연동 → 체크리스트 순서로 구성한다.

**기술 스택:** 마크다운, Claude 커스텀 커맨드 포맷

**스펙:** `docs/specs/2026-08-23-be-dev-skill-design.md`

## 전역 제약

- 기존 스킬 파일 포맷 준수: YAML frontmatter (`name`, `description`, `allowed-tools`) + 마크다운 본문
- 마크다운 파일 1개만 생성, 기존 파일 수정 없음
- 330줄 이하로 유지 (CLAUDE.md 규칙)
- `'use server'` 규칙, Actions → Service → Repository 단방향 호출 규칙을 스킬 본문에 반드시 포함
- Repository는 null 반환 / Service는 AppError throw / Actions는 ActionResult 반환 에러 흐름을 반드시 포함
- No Commits HARD GATE를 스킬 마지막 섹션에 반드시 포함

---

### 태스크 1: GitHub 이슈 생성 + 브랜치 생성 + work_history 파일 생성

**파일:**
- 생성: `work_history/2026-08-23-feature-#이슈번호-be-dev-skill.md` (이슈 생성 후 번호 확정)

**인터페이스:**
- 소비: 없음 (신규 작업 시작)
- 생산: GitHub 이슈, feature 브랜치, work_history 파일

- [ ] **스텝 1: GitHub 이슈 생성**

```bash
gh issue create \
  --title "공통/docs: 백엔드 개발 스킬 작성" \
  --body "## 개요
BE 레이어(Actions/Service/Repository) 코드 작성 시 Claude가 참고하는 행동 지침 스킬 파일을 작성한다.

## 작업 내용
- \`.claude/commands/be-dev.md\` 파일 생성
- 레이어 의사결정 트리, 공통 타입 패턴(ErrorCode/AppError/ActionResult), 레이어별 코드 패턴, Supabase Auth 연동, R2 이미지 업로드 연동, Drizzle 마이그레이션 절차, 체크리스트 포함

## 참고
- 스펙: \`docs/specs/2026-08-23-be-dev-skill-design.md\`
- 상위 이슈: #1 (개발 환경 초기 세팅)" \
  --label "setup" \
  --milestone "v0.1 - 인프라 세팅"
```

출력된 이슈 번호를 메모한다 (이하 `{N}` 으로 표기).

- [ ] **스텝 2: feature 브랜치 생성**

```bash
git checkout dev
git checkout -b feature/#{N}-be-dev-skill
```

- [ ] **스텝 3: work_history 파일 생성**

`work_history/2026-08-23-feature-#{N}-be-dev-skill.md` 를 `docs/work-history-spec.md` 규격에 따라 생성한다.
핵심 기재 항목: 이슈 번호, 브랜치명, 작업 목표, 스펙 경로.

---

### 태스크 2: 스킬 파일 뼈대 + 섹션 1 (레이어 의사결정) + 섹션 2 (공통 타입 패턴)

**파일:**
- 생성: `.claude/commands/be-dev.md`

**인터페이스:**
- 소비: 없음 (신규 파일)
- 생산: `/be-dev` 커맨드로 호출 가능한 뼈대 + 섹션 1 + 섹션 2

- [ ] **스텝 1: frontmatter + 섹션 1 작성**

```markdown
---
name: be-dev
description: BE 레이어(Actions/Service/Repository) 코드 작성 규칙. Server Action 패턴, Drizzle 쿼리, Supabase Auth 연동, R2 업로드 규칙. BE 코드 작성 시 사용한다.
allowed-tools:
  [
    'Read',
    'Write',
    'Edit',
    'Bash(npx tsc:*)',
    'Bash(npx drizzle-kit:*)',
    'mcp__ide__getDiagnostics',
  ]
---

# 백엔드 개발 스킬

## 섹션 1 — BE 레이어 의사결정

코드 작성 전 반드시 레이어를 결정한다.

```
새 BE 코드 작성 시작
│
├── 외부에서 호출되는 진입점인가? (폼 처리, 버튼 클릭, 페이지 데이터 로딩)
│   └── Yes → Actions (src/actions/)
│       입력 검증 → 인증 확인(필요 시) → Service 호출 → ActionResult 반환
│
├── 비즈니스 로직인가? (조건 판단, 계산, 외부 서비스 호출)
│   └── Yes → Service (src/services/{도메인}/)
│       Repository 호출. R2·sharp 직접 호출 가능. 없는 데이터는 AppError throw
│
├── DB 쿼리인가? (조회, 삽입, 수정, 삭제)
│   └── Yes → Repository (src/repositories/{도메인}/)
│       Drizzle 쿼리만. 데이터 없으면 null 반환
│
└── 테이블/컬럼 정의인가?
    └── Yes → DB (src/db/schema.ts)
```

**핵심 규칙**

- 레이어 간 호출: Actions → Service → Repository 단방향만 허용. 역방향·건너뛰기 금지
- Actions에서 DB 직접 접근 금지
- Repository에서 비즈니스 로직 작성 금지
```

- [ ] **스텝 2: 섹션 2 (공통 타입 패턴) 작성**

```markdown
---

## 섹션 2 — 공통 타입 패턴

### ErrorCode enum

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

### AppError 클래스

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

### ActionResult 타입

```typescript
// src/types/action.ts
export type ActionResult<T> =
  | { success: true; data: T }
  | { success: false; error: string; code: string }
```

**에러 흐름**: Repository → `null` 반환 → Service → `AppError` throw → Actions → `ActionResult` 반환 → FE Hook → `result.success` 분기
```

- [ ] **스텝 3: 중간 커밋**

```bash
git add .claude/commands/be-dev.md
git commit -m "공통/docs: be-dev 스킬 뼈대 및 레이어 의사결정·타입 패턴 섹션 추가"
```

---

### 태스크 3: 섹션 3 — 레이어별 코드 패턴 (Actions / Service / Repository)

**파일:**
- 수정: `.claude/commands/be-dev.md`

**인터페이스:**
- 소비: 태스크 2에서 생성한 파일
- 생산: Actions·Service·Repository 세 레이어의 코드 패턴이 담긴 섹션 3

- [ ] **스텝 1: 섹션 3-1 Actions 패턴 작성**

```markdown
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

**규칙**: 파일 최상단 `'use server'`. 화살표 함수. 입력 검증 → 인증 확인(필요 시) → Service 호출 순서 고정. DB·비즈니스 로직 직접 작성 금지.
```

- [ ] **스텝 2: 섹션 3-2 Service 패턴 작성**

```markdown
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

**규칙**: `export const ServiceName = { method: async () => ... }` 형태. Repository만 호출 (DB 직접 접근 금지). 데이터 없음 → `AppError` throw (null 반환 금지). R2·sharp 직접 호출 가능.
```

- [ ] **스텝 3: 섹션 3-3 Repository 패턴 작성**

```markdown
---

### 3-3. Repository

```typescript
// src/repositories/product/product.repository.ts
import { eq, desc } from 'drizzle-orm'
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
    const result: Product[] = await db.insert(products).values(data).returning()
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

**규칙**: `export const RepositoryName = { ... }` 형태. 없는 데이터는 `null` 반환 (throw 금지). Drizzle 쿼리만 작성. `returning()`으로 insert/update 결과 반환.
```

- [ ] **스텝 4: 중간 커밋**

```bash
git add .claude/commands/be-dev.md
git commit -m "공통/docs: be-dev 스킬 레이어별 코드 패턴 섹션 추가"
```

---

### 태스크 4: 섹션 4-6 — Supabase Auth + R2 업로드 + Drizzle 마이그레이션

**파일:**
- 수정: `.claude/commands/be-dev.md`

**인터페이스:**
- 소비: 태스크 3까지 완성된 파일
- 생산: 외부 서비스 연동(Supabase Auth, R2) 및 스키마 변경 절차가 담긴 섹션 4-6

- [ ] **스텝 1: 섹션 4 (Supabase Auth 연동) 작성**

```markdown
---

## 섹션 4 — Supabase Auth 연동

인증이 필요한 Action에서만 사용한다.

### 서버 클라이언트 생성 (`src/lib/supabase.ts`)

```typescript
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

### Actions에서 인증 확인

```typescript
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
    if (e instanceof AppError) return { success: false, error: e.message, code: e.code }
    return { success: false, error: '서버 오류가 발생했습니다', code: 'INTERNAL_ERROR' }
  }
}
```

**규칙**: 인증 확인은 입력 검증 직후, Service 호출 전. 비인증 시 즉시 `UNAUTHORIZED` 반환. `user.id`를 Service에 전달.
```

- [ ] **스텝 2: 섹션 5 (R2 이미지 업로드 연동) 작성**

```markdown
---

## 섹션 5 — R2 이미지 업로드 연동

Service에서 `src/lib/r2.ts` 함수를 직접 호출한다.

### Service에서 이미지 업로드

```typescript
import { uploadThumbnail, uploadDetailImage } from '@/lib/r2'

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

### Actions에서 FormData → Buffer 변환

```typescript
export const createProduct = async (formData: FormData): Promise<ActionResult<Product>> => {
  const thumbnailFile = formData.get('thumbnail') as File | null
  if (!thumbnailFile) {
    return { success: false, error: '썸네일 이미지가 필요합니다', code: 'VALIDATION_ERROR' }
  }
  const thumbnailBuffer: Buffer = Buffer.from(await thumbnailFile.arrayBuffer())
  // ... Service 호출
}
```

**규칙**: R2·sharp 호출은 Service에서만. 이미지 업로드는 DB 저장 전 수행. Actions는 File → Buffer 변환 후 Service에 전달.
```

- [ ] **스텝 3: 섹션 6 (Drizzle 스키마 변경 절차) 작성**

```markdown
---

## 섹션 6 — Drizzle 스키마 변경 절차

`src/db/schema.ts` 수정 시 반드시 마이그레이션을 실행한다.

```bash
# 1. 스키마 변경 후 마이그레이션 파일 생성
npx drizzle-kit generate

# 2. 개발 DB에 적용
npx drizzle-kit push
```

**규칙**: 스키마 변경 → generate → push 순서 준수. `drizzle-kit push`는 개발/테스트 환경에서만. 마이그레이션 파일(`src/db/migrations/`)은 git에 커밋.
```

- [ ] **스텝 4: 중간 커밋**

```bash
git add .claude/commands/be-dev.md
git commit -m "공통/docs: be-dev 스킬 Supabase Auth·R2·Drizzle 연동 섹션 추가"
```

---

### 태스크 5: 섹션 7-8 + TDD 연동 + No Commits HARD GATE + 완성 커밋 + PR

**파일:**
- 수정: `.claude/commands/be-dev.md`
- 수정: `work_history/2026-08-23-feature-#{N}-be-dev-skill.md`

**인터페이스:**
- 소비: 태스크 4까지 완성된 파일
- 생산: import 순서·체크리스트·TDD 참조·HARD GATE까지 포함한 완성 스킬 파일 + PR

- [ ] **스텝 1: 섹션 7 (import 순서) 작성**

```markdown
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
```

- [ ] **스텝 2: 섹션 8 (체크리스트) 작성**

```markdown
---

## 섹션 8 — 체크리스트

### Actions
- [ ] 파일 최상단에 `'use server'`가 있는가
- [ ] 모든 함수가 화살표 함수인가
- [ ] 입력 검증 → 인증 확인(필요 시) → Service 호출 순서인가
- [ ] `ActionResult<T>` 반환 타입이 명시되어 있는가
- [ ] `AppError`를 catch해서 `ActionResult`로 변환하는가
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

## ⛔ No Commits (HARD GATE)

**코드 작성 완료 후 자동으로 커밋하지 않는다.**
모든 체크리스트 확인 후에도 자동 커밋 금지. 사용자에게 결과를 보여주고 명시적 승인("커밋해주세요")을 받은 후에만 `git commit`을 실행한다.
```

- [ ] **스텝 3: 줄 수 확인**

```bash
wc -l .claude/commands/be-dev.md
```

330줄 초과 시: 섹션 5 FormData 변환 예시 코드 단축 또는 섹션 3 Repository update/delete 메서드 생략으로 조정한다.

- [ ] **스텝 4: 최종 커밋**

```bash
git add .claude/commands/be-dev.md
git commit -m "공통/docs: 백엔드 개발 스킬 작성 closes #{N}"
```

- [ ] **스텝 5: work_history 파일 업데이트**

`work_history/2026-08-23-feature-#{N}-be-dev-skill.md`에 완료 내용(커밋 목록, 변경 파일) 기록.

- [ ] **스텝 6: PR 생성**

```bash
git push -u origin feature/#{N}-be-dev-skill
gh pr create \
  --title "공통/docs: 백엔드 개발 스킬 작성" \
  --base dev \
  --body "## 개요
BE 레이어(Actions/Service/Repository) 코드 작성 시 Claude가 참고하는 행동 지침 스킬 파일 `.claude/commands/be-dev.md`를 추가한다.

## 주요 내용
- 레이어 의사결정 트리 (Actions → Service → Repository 단방향 규칙)
- 공통 타입 패턴 (ErrorCode enum / AppError / ActionResult<T>)
- 레이어별 코드 패턴 (Actions Server Action, Service, Repository Drizzle 쿼리)
- Supabase Auth 연동 (createSupabaseServerClient + getUser 패턴)
- R2 이미지 업로드 연동 (Service에서 uploadThumbnail / uploadDetailImage 호출)
- Drizzle 스키마 변경 절차 (generate → push)
- 섹션별 체크리스트 + TDD 연동 + No Commits HARD GATE

## 스펙
\`docs/specs/2026-08-23-be-dev-skill-design.md\`

closes #{N}"
```

- [ ] **스텝 7: work_history에 PR URL 기록**

`work_history/2026-08-23-feature-#{N}-be-dev-skill.md`에 PR URL 업데이트.

---

## 셀프 리뷰

**스펙 커버리지 점검:**
- [x] 스킬 메타데이터 (frontmatter, allowed-tools: tsc, drizzle-kit, getDiagnostics) → 태스크 2
- [x] 섹션 1 레이어 의사결정 트리 → 태스크 2 스텝 1
- [x] 섹션 2 공통 타입 (ErrorCode / AppError / ActionResult) → 태스크 2 스텝 2
- [x] 섹션 3-1 Actions 코드 패턴 (`'use server'`, 화살표 함수, ActionResult 반환) → 태스크 3 스텝 1
- [x] 섹션 3-2 Service 코드 패턴 (AppError throw, Repository 호출) → 태스크 3 스텝 2
- [x] 섹션 3-3 Repository 코드 패턴 (Drizzle eq/desc, null 반환, returning()) → 태스크 3 스텝 3
- [x] 섹션 4 Supabase Auth (createSupabaseServerClient + getUser) → 태스크 4 스텝 1
- [x] 섹션 5 R2 이미지 업로드 (Service에서 호출, FormData → Buffer) → 태스크 4 스텝 2
- [x] 섹션 6 Drizzle 스키마 변경 절차 → 태스크 4 스텝 3
- [x] 섹션 7 import 순서 → 태스크 5 스텝 1
- [x] 섹션 8 체크리스트 (Actions/Service/Repository/공통) → 태스크 5 스텝 2
- [x] TDD 연동 (`/tdd-be` 참조) → 태스크 5 스텝 2
- [x] No Commits HARD GATE → 태스크 5 스텝 2

**플레이스홀더 스캔:** TBD, TODO 없음. `{N}` 은 실행 시 확정되는 이슈 번호로, 플레이스홀더가 아닌 실행 지시임. 모든 스텝에 실제 마크다운/커맨드 포함.

**타입 일관성:** `ActionResult<T>` — 섹션 2에서 정의, 섹션 3-1·4에서 동일 타입 사용. `AppError` — 섹션 2에서 정의, 섹션 3-2·4에서 동일 클래스 사용. `Product | null` (Repository) vs `Product` (Service) 반환 타입 일관.
