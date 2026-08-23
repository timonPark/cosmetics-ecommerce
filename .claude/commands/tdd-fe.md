---
name: tdd-fe
description: FE 레이어 TDD 구현. Component와 Hook 단위 테스트를 소스 파일 옆(코로케이션)에 작성한다. 실패 케이스 → 성공 케이스 → 구현 순서로 진행한다.
allowed-tools:
  [
    'Read',
    'Write',
    'Edit',
    'Bash(npx jest:*)',
    'Bash(npx tsc:*)',
    'mcp__ide__getDiagnostics',
  ]
---

# FE TDD 스킬

## TDD 사이클 (단위 반복)

```
1. 컴포넌트/훅 스텁 작성    → 최소 구조만 존재, 실제 동작 없음
2. 실패 케이스 테스트 작성   → npx jest 실행 → 실패 케이스 PASS 확인
3. 성공 케이스 테스트 추가   → npx jest 실행 → 성공 케이스 FAIL 확인 (Red)
4. 구현                     → npx jest 실행 → 전체 PASS 확인 (Green)
```

> **규칙**: 성공 케이스 테스트를 작성하기 전에 반드시 실패 케이스가 먼저 통과하는지 확인한다.

---

## 파일 위치 규칙 (코로케이션)

| 레이어 | 소스 경로 | 테스트 경로 |
|--------|-----------|-------------|
| Component | `src/components/{도메인}/{ComponentName}.tsx` | `src/components/{도메인}/{ComponentName}.test.tsx` |
| Hook | `src/hooks/{hookName}.ts` | `src/hooks/{hookName}.test.ts` |

---

## Component 테스트 파일 구조

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// ── Server Actions mock ──
jest.mock('../../actions/product.actions', () => ({
    addToCart: jest.fn(),
}));

// ── import (mock 선언 이후) ──
import { ProductCard } from './ProductCard';
import type { Product } from '../../types/product';

// ── mock 함수 참조 ──
const mockAddToCart = jest.requireMock('../../actions/product.actions')
    .addToCart as jest.Mock;

// ── Stub factory ──
const makeProduct = (overrides: Partial<Product> = {}): Product => ({
    id: 'product-id-1',
    name: '수분 크림',
    price: 35000,
    thumbnailUrl: 'https://example.com/image.webp',
    isAvailable: true,
    ...overrides,
});
```

---

## Hook 테스트 파일 구조

```typescript
import { renderHook, act } from '@testing-library/react';

// ── Server Actions mock ──
jest.mock('../actions/cart.actions', () => ({
    addToCart: jest.fn(),
    removeFromCart: jest.fn(),
}));

// ── import (mock 선언 이후) ──
import { useCart } from './useCart';

// ── mock 함수 참조 ──
const mockAddToCart = jest.requireMock('../actions/cart.actions')
    .addToCart as jest.Mock;
```

> **주의**: Hook 테스트는 반드시 `renderHook`을 사용한다. Hook을 컴포넌트 외부에서 직접 호출하면 React 규칙 위반 오류가 발생한다.

---

## 실패 케이스 작성 패턴 (Component)

```typescript
describe('ProductCard', () => {
    afterEach(() => jest.clearAllMocks());

    describe('실패 케이스', () => {
        it('E1: isAvailable이 false이면 장바구니 버튼이 비활성화된다', () => {
            const product: Product = makeProduct({ isAvailable: false });
            render(<ProductCard product={product} />);

            const button = screen.getByRole('button', { name: /장바구니/ });
            expect(button).toBeDisabled();
        });

        it('E2: thumbnailUrl이 없으면 대체 이미지가 렌더링된다', () => {
            const product: Product = makeProduct({ thumbnailUrl: '' });
            render(<ProductCard product={product} />);

            const img = screen.getByRole('img');
            expect(img).toHaveAttribute('src', expect.stringContaining('placeholder'));
        });
    });
```

실패 케이스 실행 → **E1, E2 PASS** 확인 후 성공 케이스 추가.

---

## 성공 케이스 작성 패턴 (Component)

```typescript
    describe('성공 케이스', () => {
        it('S1: 상품 정보가 올바르게 렌더링된다', () => {
            const product: Product = makeProduct();
            render(<ProductCard product={product} />);

            expect(screen.getByText(product.name)).toBeInTheDocument();
            expect(screen.getByText('35,000원')).toBeInTheDocument();
        });

        it('S2: 장바구니 버튼 클릭 시 addToCart가 호출된다', async () => {
            const product: Product = makeProduct();
            render(<ProductCard product={product} />);

            await userEvent.click(screen.getByRole('button', { name: /장바구니/ }));

            expect(mockAddToCart).toHaveBeenCalledWith(product.id);
        });
    });
```

---

## 실패 케이스 작성 패턴 (Hook)

```typescript
describe('useCart', () => {
    afterEach(() => jest.clearAllMocks());

    describe('실패 케이스', () => {
        it('E1: addItem 호출 시 Server Action 오류면 error 상태가 설정된다', async () => {
            mockAddToCart.mockRejectedValue(new Error('서버 오류'));

            const { result } = renderHook(() => useCart());

            await act(async () => {
                await result.current.addItem('product-id-1');
            });

            expect(result.current.error).toBe('서버 오류');
            expect(result.current.items).toHaveLength(0);
        });
    });
```

---

## 성공 케이스 작성 패턴 (Hook)

```typescript
    describe('성공 케이스', () => {
        it('S1: addItem 호출 시 items에 상품이 추가된다', async () => {
            mockAddToCart.mockResolvedValue({ success: true });

            const { result } = renderHook(() => useCart());

            await act(async () => {
                await result.current.addItem('product-id-1');
            });

            expect(result.current.items).toHaveLength(1);
            expect(result.current.error).toBeNull();
        });
    });
```

---

## 테스트 실행 명령어

```bash
# Component 테스트
npx jest src/components/{도메인}/{ComponentName}.test.tsx --forceExit
npx jest src/components/{도메인}/{ComponentName}.test.tsx --forceExit -t "실패 케이스"

# Hook 테스트
npx jest src/hooks/{hookName}.test.ts --forceExit

# 전체 FE 테스트
npx jest src/ --forceExit
```

---

## 체크리스트

- [ ] 스텁이 최소 구조만 가지고 실제 동작은 없는가
- [ ] 실패 케이스(E1~)가 먼저 PASS하는 것을 확인했는가
- [ ] 성공 케이스(S1~)가 구현 전 FAIL하는 것을 확인했는가 (Red)
- [ ] 구현 후 전체 케이스가 PASS하는가 (Green)
- [ ] `jest.requireMock`으로 mock 함수를 참조하는가
- [ ] Hook 테스트에서 `renderHook`과 `act`를 사용하는가
- [ ] `afterEach(() => jest.clearAllMocks())`가 있는가
- [ ] 모든 변수·함수·반환값에 TypeScript 타입이 명시되어 있는가
- [ ] 테스트 파일이 소스 파일과 같은 폴더에 위치하는가 (코로케이션)

---

## ⛔ No Commits (HARD GATE)

**테스트 사이클 완료 후 자동으로 커밋하지 않는다.**
- 모든 테스트가 통과(Green)해도 자동 커밋 금지.
- 테스트 결과를 사용자에게 보여주고 명시적 승인("커밋해주세요")을 받은 후에만 `git commit`을 실행한다.
