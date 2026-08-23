# 설계 문서: 테스트 환경 세팅 (Jest + React Testing Library)

- 작성일: 2026-08-23
- 이슈: #15
- 브랜치: `feature/#15-jest-setup`

---

## 개요

Next.js 16 App Router + TypeScript + React 19 프로젝트에 Jest + React Testing Library 기반 테스트 환경을 구성한다. BE 단위/통합 테스트와 FE 컴포넌트/훅 테스트를 모두 지원하며, `tdd-be` / `tdd-fe` 스킬의 실행 기반이 된다.

---

## 선택 접근법

**`next/jest` + 단일 config + 도큐블록 방식**

- `next/jest`의 `createJestConfig`로 App Router 호환 처리(SWC 트랜스폼, 경로 별칭, Server Component 처리)를 자동화한다.
- 기본 `testEnvironment`는 `node` (BE 테스트 기본값).
- FE 테스트 파일 상단에 `/** @jest-environment jsdom */` 도큐블록을 추가해 환경을 개별 지정한다.

---

## 설치 패키지

```
devDependencies 추가:
  jest
  jest-environment-jsdom
  @testing-library/react        # React 19 지원 v16+
  @testing-library/jest-dom
  @testing-library/user-event
  @types/jest
```

---

## 파일 구성

### 신규 생성 파일

```
jest.config.ts                  # Jest 설정 (next/jest createJestConfig)
jest.setup.ts                   # jest-dom import
__tests__/
  unit/
    services/                   # BE 단위 테스트 (Repository mock)
  integration/
    repositories/               # BE 통합 테스트 (실제 TEST_DATABASE_URL)
```

### 수정 파일

```
tsconfig.json                   # include에 "__tests__/**/*" 추가
package.json                    # test 스크립트 추가
```

### FE 테스트 위치 (기존 규칙 유지)

컴포넌트·훅 테스트는 소스 파일 옆 코로케이션:
```
src/components/product/ProductCard.tsx
src/components/product/ProductCard.test.tsx   ← 여기에 위치
```

---

## jest.config.ts 구조

```ts
import type { Config } from 'jest'
import nextJest from 'next/jest'

const createJestConfig = nextJest({ dir: './' })

const config: Config = {
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
}

export default createJestConfig(config)
```

---

## npm scripts

| 스크립트 | 실행 범위 | 비고 |
|---------|---------|------|
| `test` | `__tests__/unit` + `src` | CI 기본 실행 (DB 불필요) |
| `test:unit` | `__tests__/unit` | BE 단위 테스트만 |
| `test:integration` | `__tests__/integration` | BE 통합 테스트 (TEST_DATABASE_URL 필요) |
| `test:fe` | `src` | FE 테스트만 |
| `test:watch` | 전체 | 개발 중 watch 모드 |

```json
"test": "jest --testPathPattern='__tests__/unit|src'",
"test:unit": "jest __tests__/unit",
"test:integration": "jest __tests__/integration",
"test:fe": "jest src",
"test:watch": "jest --watch"
```

---

## 환경변수 전략

### 파일

```
.env.test.local    # gitignore 포함 — 로컬 전용
```

### 내용

```
TEST_DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[db]?sslmode=require
```

### 로드 방법

`jest.config.ts`에서 `setupFiles`에 dotenv 로드를 추가해 통합 테스트 실행 전 자동 주입:

```ts
setupFiles: ['<rootDir>/jest.env.setup.ts'],   // dotenv 로드 전용
```

`jest.env.setup.ts`:
```ts
import { config } from 'dotenv'
config({ path: '.env.test.local' })
```

### Supabase 테스트 프로젝트

- Supabase에 테스트 전용 프로젝트를 별도 생성한다.
- 스키마는 운영 프로젝트와 동일하게 마이그레이션을 적용한다.
- `TEST_DATABASE_URL`에는 Supabase 테스트 프로젝트의 Session Pooler URL을 사용한다.

---

## tsconfig.json 수정

`include` 배열에 `"__tests__/**/*"` 추가:

```json
"include": [
  "next-env.d.ts",
  "**/*.ts",
  "**/*.tsx",
  ".next/types/**/*.ts",
  ".next/dev/types/**/*.ts",
  "**/*.mts",
  "__tests__/**/*"
]
```

---

## 동작 확인용 샘플 테스트

설치 완료 후 아래 파일로 환경 검증:

```
__tests__/unit/services/sample.test.ts
```

```ts
describe('sample', () => {
  it('테스트 환경이 정상 동작한다', () => {
    expect(1 + 1).toBe(2)
  })
})
```

`npm test` 통과 확인 후 삭제.

---

## 완료 기준

- [ ] `npm test` 실행 시 오류 없이 통과
- [ ] `npm run test:integration` 실행 시 `TEST_DATABASE_URL` 없으면 DB 연결 오류로 실패 (의도된 동작)
- [ ] FE 테스트 파일에서 `@testing-library/jest-dom` matcher (`toBeInTheDocument` 등) 사용 가능
- [ ] `@/*` 경로 별칭이 테스트 파일에서 정상 동작
