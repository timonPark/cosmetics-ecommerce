---
name: tdd-be
description: BE 레이어 TDD 구현. Service 단위 테스트(Repository mock)와 Repository 통합 테스트(실제 DB)를 작성한다. 실패 케이스 → 성공 케이스 → 구현 순서로 진행한다.
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

# BE TDD 스킬

## TDD 사이클 (메서드 단위 반복)

```
1. 메서드 스텁 작성        → throw new Error('not implemented')
2. 실패 케이스 테스트 작성  → npx jest 실행 → 실패 케이스 PASS 확인
3. 성공 케이스 테스트 추가  → npx jest 실행 → 성공 케이스 FAIL 확인 (Red)
4. 로직 구현               → npx jest 실행 → 전체 PASS 확인 (Green)
```

> **규칙**: 성공 케이스 테스트를 작성하기 전에 반드시 실패 케이스가 먼저 통과하는지 확인한다.

---

## 파일 위치 규칙

| 레이어 | 테스트 경로 | 소스 경로 |
|--------|-------------|-----------|
| Service (단위) | `__tests__/unit/services/{도메인}/{파일명}.service.test.ts` | `src/services/{도메인}/{파일명}.service.ts` |
| Repository (통합) | `__tests__/integration/repositories/{도메인}/{파일명}.repository.test.ts` | `src/repositories/{도메인}/{파일명}.repository.ts` |

---

## Service 테스트 파일 구조

```typescript
// ── 1. Repository mock ──
jest.mock('../../../src/repositories/product/product.repository', () => ({
    ProductRepository: {
        findById: jest.fn(),
        findAll: jest.fn(),
        save: jest.fn(),
        delete: jest.fn(),
    },
}));

// ── 2. 외부 서비스 mock (R2, sharp 등) ──
jest.mock('../../../src/lib/r2', () => ({
    uploadImage: jest.fn(),
    deleteImage: jest.fn(),
}));

// ── 3. import (mock 선언 이후) ──
import { ProductService } from '../../../src/services/product/product.service';
import { ErrorCode } from '../../../src/types/error-code.enum';

// ── 4. mock 함수 참조 (jest.requireMock — IDE 타입 오류 방지) ──
const mockProductRepo = jest.requireMock(
    '../../../src/repositories/product/product.repository'
).ProductRepository;
const mockFindById = mockProductRepo.findById as jest.Mock;
```

> **주의**: `import` 후 `.property`로 직접 참조하면 IDE TS 서버 캐시로 인한 타입 오류가 발생할 수 있다. `jest.requireMock` 패턴을 사용한다.

---

## Repository 테스트 파일 구조

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { ProductRepository } from '../../../src/repositories/product/product.repository';
import * as schema from '../../../src/db/schema';

// 테스트 DB 연결 (환경변수: TEST_DATABASE_URL)
const client = postgres(process.env.TEST_DATABASE_URL!);
const db = drizzle(client, { schema });

beforeAll(async () => {
    // 테스트 데이터 초기화
});

afterAll(async () => {
    await client.end();
});

afterEach(async () => {
    // 각 테스트 후 데이터 정리
});
```

> **주의**: Repository 통합 테스트는 실제 테스트 DB에 연결한다. `TEST_DATABASE_URL` 환경변수가 반드시 설정되어 있어야 한다.

---

## 실패 케이스 작성 패턴 (Service)

```typescript
describe('ProductService.findById', () => {
    afterEach(() => jest.clearAllMocks());

    describe('실패 케이스', () => {
        it('E1: id가 빈 문자열이면 VALIDATION_ERROR throw', async () => {
            await expect(
                ProductService.findById(''),
            ).rejects.toMatchObject({ code: ErrorCode.VALIDATION_ERROR });
            expect(mockFindById).not.toHaveBeenCalled();
        });

        it('E2: 존재하지 않는 id면 NOT_FOUND throw', async () => {
            mockFindById.mockResolvedValue(null);
            await expect(
                ProductService.findById('non-existent-id'),
            ).rejects.toMatchObject({ code: ErrorCode.NOT_FOUND });
        });
    });
```

실패 케이스 실행 → **E1, E2 PASS** 확인 후 성공 케이스 추가.

---

## 성공 케이스 작성 패턴 (Service)

```typescript
    describe('성공 케이스', () => {
        it('S1: 정상 조회 시 상품 정보가 올바르게 반환된다', async () => {
            const stub = makeProduct();
            mockFindById.mockResolvedValue(stub);

            const result: Product = await ProductService.findById(stub.id);

            expect(result.id).toBe(stub.id);
            expect(result.name).toBe(stub.name);
            expect(result.price).toBe(stub.price);
        });
    });
```

성공 케이스 실행 → **S1 FAIL** 확인 (Red) → 구현 → **S1 PASS** 확인 (Green).

> Stub factory 패턴은 아래 참고.

---

## Stub Factory 패턴

```typescript
interface ProductStub {
    id: string;
    name: string;
    price: number;
    thumbnailUrl: string;
    isAvailable: boolean;
    createdAt: Date;
}

const makeProduct = (overrides: Partial<ProductStub> = {}): ProductStub => ({
    id: 'product-id-1',
    name: '수분 크림',
    price: 35000,
    thumbnailUrl: 'https://example.com/image.webp',
    isAvailable: true,
    createdAt: new Date(),
    ...overrides,
});
```

---

## 테스트 실행 명령어

```bash
# Service 단위 테스트
npx jest __tests__/unit/services/{도메인}/{파일명}.service.test.ts --forceExit
npx jest __tests__/unit/services/{도메인}/{파일명}.service.test.ts --forceExit -t "실패 케이스"

# Repository 통합 테스트
npx jest __tests__/integration/repositories/{도메인}/{파일명}.repository.test.ts --forceExit

# 전체 테스트
npx jest --forceExit
```

---

## 체크리스트

- [ ] 메서드 스텁이 `throw new Error('not implemented')`로 시작하는가
- [ ] 실패 케이스(E1~)가 먼저 PASS하는 것을 확인했는가
- [ ] 성공 케이스(S1~)가 구현 전 FAIL하는 것을 확인했는가 (Red)
- [ ] 구현 후 전체 케이스가 PASS하는가 (Green)
- [ ] Service 테스트에서 `jest.requireMock`으로 mock 함수를 참조하는가
- [ ] `afterEach(() => jest.clearAllMocks())`가 있는가
- [ ] 모든 변수·함수·반환값에 TypeScript 타입이 명시되어 있는가
- [ ] Repository 통합 테스트에 `TEST_DATABASE_URL`이 설정되어 있는가

---

## ⛔ No Commits (HARD GATE)

**테스트 사이클 완료 후 자동으로 커밋하지 않는다.**
- 모든 테스트가 통과(Green)해도 자동 커밋 금지.
- 테스트 결과를 사용자에게 보여주고 명시적 승인("커밋해주세요")을 받은 후에만 `git commit`을 실행한다.
