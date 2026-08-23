# 프론트엔드 개발 스킬 설계

작성일: 2026-08-23

## 개요

Claude가 FE 코드(Page/Component/Hook)를 작성하거나 Figma 디자인을 구현할 때 따르는 행동 지침 스킬 문서.

---

## 스킬 메타데이터

| 항목 | 내용 |
|------|------|
| 파일 위치 | `.claude/commands/fe-dev.md` |
| name | `fe-dev` |
| description | FE 레이어(Page/Component/Hook) 코드 작성 및 Figma 디자인 구현 규칙. FE 코드 작성, 컴포넌트 생성, 디자인 반영 작업 시 사용. |
| allowed-tools | `Read`, `Write`, `Edit`, `Bash(npx tsc:*)`, `mcp__ide__getDiagnostics`, Figma MCP 3종 |

---

## 섹션 1 — FE 레이어 의사결정 기준

코드 작성 전 레이어를 결정하는 흐름.

### 결정 트리

```
새 FE 코드 작성 시작
│
├── 라우트 파일인가? (app/ 하위 page.tsx, layout.tsx)
│   └── Yes → Page (서버 컴포넌트). default export 허용(Next.js 요구사항)
│
├── "use client" 없이 순수 렌더링만 하는가?
│   └── Yes → Component (서버 컴포넌트 가능)
│
└── 클라이언트 상태/사이드이펙트/인터랙션이 있는가?
    ├── 상태·Server Actions 호출 있음 → Hook으로 로직 분리 + Component는 렌더링만
    └── 단순 이벤트 핸들러만 → "use client" Component (Hook 불필요)
```

### 핵심 규칙

- Server Actions 호출은 **Hook에서만** — Component에서 직접 호출 금지
- `"use client"` 선언은 파일 최상단 첫 줄
- Page는 데이터를 fetching 후 Component에 props로 전달 — Page 내부에 UI 로직 작성 금지

---

## 섹션 2 — 레이어별 코드 패턴

### 2-1. Page (서버 컴포넌트)

```typescript
// src/app/(shop)/products/page.tsx
import { getProducts } from '@/actions/product.actions'
import { ProductList } from '@/components/product/ProductList'
import type { Product } from '@/types/product'

export default async function ProductsPage(): Promise<JSX.Element> {
  const products: Product[] = await getProducts()
  return <ProductList products={products} />
}
```

**규칙**:
- `default export` (Next.js App Router 요구사항 — 라우트 파일 한정 예외)
- `async` 함수로 데이터 패칭 직접 수행
- UI 로직·상태 없음. Component에 props 전달만

### 2-2. Component

```typescript
// src/components/product/ProductCard.tsx
import Image from 'next/image'
import type { Product } from '@/types/product'

type Props = {
  product: Product
  onAddToCart: (id: string) => void
}

export function ProductCard({ product, onAddToCart }: Props): JSX.Element {
  return (
    <div className="flex flex-col gap-2 rounded-lg border p-4">
      <Image
        src={product.thumbnailUrl}
        alt={product.name}
        width={300}
        height={300}
        className="rounded-md object-cover"
      />
      <p className="font-medium">{product.name}</p>
      <button
        onClick={() => onAddToCart(product.id)}
        disabled={!product.isAvailable}
      >
        장바구니 담기
      </button>
    </div>
  )
}
```

**규칙**:
- `named export` + 함수 선언식
- Props 타입은 파일 내 인라인 정의 (`type Props = { ... }`)
- 이미지는 반드시 `next/image`의 `<Image>` 사용
- 비즈니스 로직·Server Actions 호출 금지 — Hook에서 받은 콜백만 호출

### 2-3. Hook

```typescript
// src/hooks/useCart.ts
'use client'

import { useState } from 'react'
import { addToCart } from '@/actions/cart.actions'

type CartState = {
  items: string[]
  error: string | null
  addItem: (productId: string) => Promise<void>
}

export const useCart = (): CartState => {
  const [items, setItems] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  const addItem = async (productId: string): Promise<void> => {
    try {
      await addToCart({ productId })
      setItems((prev: string[]) => [...prev, productId])
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '오류가 발생했습니다')
    }
  }

  return { items, error, addItem }
}
```

**규칙**:
- `'use client'` 파일 최상단
- 화살표 함수 (컴포넌트 제외 모든 함수는 화살표 함수)
- 반환 타입을 별도 `type`으로 정의 후 명시
- Server Actions import는 Hook에서만

---

## 섹션 3 — shadcn/ui 활용 패턴

### 사용 원칙

| 상황 | 처리 방법 |
|------|-----------|
| 기본 사용 | `src/components/ui/` 에서 import해서 그대로 사용 |
| 스타일 변형 필요 | `src/components/{도메인}/` 에 래퍼 컴포넌트 생성 |
| `src/components/ui/` 직접 수정 | **금지** — CLI 재생성 시 덮어씌워짐 |

### 래퍼 컴포넌트 패턴

```typescript
// src/components/product/PrimaryButton.tsx
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { ComponentProps } from 'react'

type Props = ComponentProps<typeof Button> & {
  fullWidth?: boolean
}

export function PrimaryButton({ fullWidth = false, className, ...props }: Props): JSX.Element {
  return (
    <Button
      className={cn('bg-rose-500 hover:bg-rose-600', fullWidth && 'w-full', className)}
      {...props}
    />
  )
}
```

### 조건부 클래스 병합

```typescript
// cn() 유틸 사용 — 조건부 클래스는 항상 cn()으로 처리
className={cn('base-class', isActive && 'active-class', className)}
```

---

## 섹션 4 — Figma 디자인 반영 절차

Figma URL 또는 nodeId가 제공된 경우 아래 5단계를 순서대로 실행한다.

### 단계 1: 디자인 컨텍스트 수집

```
mcp__claude_ai_Figma__get_design_context(fileKey, nodeId)   → 레이아웃·스타일 속성
mcp__claude_ai_Figma__get_screenshot(nodeId)                → 시각적 참조 이미지
mcp__claude_ai_Figma__get_metadata(fileKey)                 → 컴포넌트 구조 및 이름
```

- `fileKey`: Figma URL의 `/design/{fileKey}/` 부분
- `nodeId`: URL의 `?node-id=` 파라미터

### 단계 2: 컴포넌트 분해

Figma 구조를 FE 레이어로 매핑한다.

| Figma 요소 | FE 레이어 |
|------------|-----------|
| 최상위 프레임/페이지 | Page |
| 반복되는 카드·아이템 | Component (재사용) |
| 모달·드로워·오버레이 | Component + Hook |
| 버튼 클릭·폼 제출 | Hook (Server Actions 호출) |

### 단계 3: shadcn/ui 매핑

Figma 요소와 shadcn/ui 컴포넌트 대응을 확인한다.

| Figma 요소 | shadcn/ui 컴포넌트 |
|------------|-------------------|
| 버튼 | `Button` |
| 입력 필드 | `Input` |
| 선택 드롭다운 | `Select` |
| 다이얼로그/모달 | `Dialog` |
| 없는 경우 | Tailwind로 직접 구현 또는 래퍼 생성 |

### 단계 4: 구현

- 섹션 1 의사결정 트리로 레이어 결정
- 섹션 2 코드 패턴으로 구현
- Tailwind 클래스는 Figma 수치 기반으로 작성
  - spacing: Figma px ÷ 4 → Tailwind 단위 (예: 16px → `p-4`)
  - 색상: Figma 색상 → Tailwind 색상 토큰 또는 hex 직접 사용

### 단계 5: 시각적 검증

```
mcp__claude_ai_Figma__get_screenshot(nodeId)  → Figma 원본 재확인
```

- 레이아웃 구조 일치 여부 확인
- 간격·폰트·색상 주요 불일치 항목 목록화
- 불일치 항목 수정 후 사용자에게 보고

---

## 섹션 5 — import 순서

```typescript
// 1. React / Next.js
import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'

// 2. 외부 라이브러리
import { cn } from 'class-variance-authority'

// 3. 내부 모듈 — 절대 경로 (@/)
import { Button } from '@/components/ui/button'
import type { Product } from '@/types/product'

// 4. 상대 경로
import { ProductCard } from './ProductCard'
```

그룹 사이 빈 줄 하나. type import는 `import type`으로 분리.

---

## 섹션 6 — 체크리스트

### 레이어 결정

- [ ] 의사결정 트리를 따라 레이어를 결정했는가
- [ ] Server Actions 호출이 Hook에만 있는가
- [ ] `"use client"` 선언이 필요한 파일에만, 최상단에 있는가

### Component

- [ ] `named export` + 함수 선언식인가 (라우트 파일 제외)
- [ ] Props 타입이 `type Props = { ... }` 로 명시되어 있는가
- [ ] 이미지가 `<Image>` (next/image) 로 구현되었는가
- [ ] Component 내부에 비즈니스 로직이 없는가

### Hook

- [ ] 파일 최상단에 `'use client'` 가 있는가
- [ ] 반환 타입이 별도 type으로 정의되어 있는가
- [ ] 모든 변수·함수에 TypeScript 타입이 명시되어 있는가

### shadcn/ui

- [ ] `src/components/ui/` 파일을 직접 수정하지 않았는가
- [ ] 커스터마이징이 래퍼 컴포넌트로 분리되어 있는가

### Figma (디자인 구현 시)

- [ ] `get_design_context`로 레이아웃·스타일 정보를 수집했는가
- [ ] 컴포넌트 분해가 레이어 규칙에 맞게 이루어졌는가
- [ ] `get_screenshot`으로 시각적 검증을 완료했는가

### 공통

- [ ] import 순서 규칙을 따르는가
- [ ] `npx tsc --noEmit` 통과하는가

---

## TDD 연동

FE 코드 작성 후 테스트 작성은 `/tdd-fe` 스킬을 사용한다.

- Component → `{ComponentName}.test.tsx` 코로케이션
- Hook → `{hookName}.test.ts` 코로케이션

---

## 범위 외

- BE 레이어(Actions/Service/Repository) 작성 → `/tdd-be` 스킬
- GitHub 이슈·브랜치 관리 → `/github-project` 스킬
