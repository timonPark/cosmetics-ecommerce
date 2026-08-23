# 코딩 규칙

## 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 컴포넌트 파일 | PascalCase | `ProductCard.tsx` |
| 파일/폴더 (컴포넌트 외) | kebab-case | `product-list/`, `use-cart.ts` |
| 변수·함수 | camelCase | `productName`, `getProduct()` |
| 타입·인터페이스 | PascalCase | `Product`, `ProductFilter` |
| 상수 | UPPER_SNAKE_CASE | `MAX_UPLOAD_SIZE`, `DEFAULT_PAGE_SIZE` |
| DB 컬럼 (Drizzle 스키마) | snake_case | `created_at`, `thumbnail_url` |
| Enum 값 | UPPER_SNAKE_CASE | `ErrorCode.NOT_FOUND` |

- 서버 컴포넌트 우선, 클라이언트 컴포넌트는 `"use client"` 명시
- 이미지는 반드시 Next.js `<Image>` 컴포넌트 사용

## 타입 명시 규칙

변수, 함수, 클래스 등 모든 경우에 TypeScript 타입을 명시한다. 타입 추론에 의존하지 않는다.

```typescript
// ✅ 변수
const productName: string = '수분 크림'
const price: number = 35000

// ✅ 함수 — 파라미터와 반환 타입 모두 명시
function getProduct(id: string): Promise<Product> { ... }
const formatPrice = (price: number): string => `${price.toLocaleString()}원`

// ✅ 객체·배열
const filters: ProductFilter = { category: 'skincare', minPrice: 0 }
const ids: string[] = ['a', 'b', 'c']

// ❌ 타입 추론에 의존
const productName = '수분 크림'
const getProduct = async (id) => { ... }
```

## 커밋 메시지 규칙

```
feat: 새 기능
fix: 버그 수정
chore: 설정/도구 변경
docs: 문서 변경
refactor: 리팩토링
style: 스타일(UI) 변경
perf: 성능 개선
```

이슈 연결: 커밋/PR에 `closes #이슈번호` 표기 → 머지 시 이슈 자동 닫힘

### 작업 분류 코드

커밋 메시지와 이슈 제목에 도메인을 함께 표기한다: `{도메인}/{식별값}: 내용`

| 도메인 | 식별값 | 설명 |
|--------|--------|------|
| BE | `feat` | 기능 개발 — 새 API, Service, DB 스키마, 외부 서비스 연동 |
| BE | `fix` | 버그 수정 — 잘못된 쿼리, 비즈니스 로직 오류 |
| BE | `refactor` | 리팩토링 — 레이어 구조 개선 (동작 변경 없음) |
| BE | `perf` | 성능 개선 — 쿼리 최적화, 이미지 처리 성능 |
| FE | `feat` | 화면 기능 개발 — 새 페이지, 컴포넌트, 인터랙션 |
| FE | `fix` | 버그 및 기능 수정 — 잘못된 UI 동작, 렌더링 오류 |
| FE | `style` | 화면 개선 및 디자인 변경 — UI/UX 개선, 스타일 변경 |
| FE | `perf` | 성능 개선 — 렌더링 최적화, 번들 최적화 |
| 공통 | `chore` | 환경 설정 — 패키지 설치, 환경변수, 빌드 설정 |
| 공통 | `docs` | 문서 작업 — CLAUDE.md, 스펙 문서, 개발 규칙 |

**예시**: `BE/feat: 상품 조회 Service 구현 closes #15`

## 코드 스타일 가이드

### import 순서

아래 순서를 지키고 그룹 사이에 빈 줄을 둔다.

```typescript
// 1. React / Next.js
import { useState } from 'react'
import Image from 'next/image'

// 2. 외부 라이브러리
import { eq } from 'drizzle-orm'

// 3. 내부 모듈 — 절대 경로 (@/)
import { ProductService } from '@/services/product/product.service'
import type { Product } from '@/types/product'

// 4. 상대 경로
import { ProductCard } from './ProductCard'
```

### 함수 스타일

- **컴포넌트**: 함수 선언식 — React DevTools 이름 표시, hoisting 보장
- **그 외 모든 함수**: 화살표 함수로 통일 (유틸리티, 핸들러, Service 메서드, Hook 내부 등)

```typescript
// ✅ 컴포넌트 — 함수 선언식
export function ProductCard({ product }: Props): JSX.Element { ... }

// ✅ 그 외 — 화살표 함수
const formatPrice = (price: number): string => `${price.toLocaleString()}원`
const handleClick = async (): Promise<void> => { ... }
```

### 컴포넌트 파일 구조

```typescript
// 1. import
import type { Product } from '@/types/product'

// 2. 타입 정의
type Props = {
  product: Product
  onAddToCart: (id: string) => void
}

// 3. 컴포넌트 (named export, 함수 선언식)
export function ProductCard({ product, onAddToCart }: Props): JSX.Element {
  return (...)
}
```

- `default export` 금지 — named export만 사용
- Props 타입은 컴포넌트 파일 안에 정의. 외부에서 재사용되는 경우만 `types/`로 분리

### Server Action 파일 구조

```typescript
'use server'

// 1. import
import { ProductService } from '@/services/product/product.service'
import type { ActionResult } from '@/types/action'

// 2. 입력 타입
type GetProductInput = {
  id: string
}

// 3. Action 함수 (화살표 함수)
export const getProduct = async (input: GetProductInput): Promise<ActionResult<Product>> => {
  // 유효성 검사 → Service 호출 → 결과 반환
}
```
