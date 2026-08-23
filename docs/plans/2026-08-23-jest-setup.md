# Jest + React Testing Library 테스트 환경 세팅 구현 계획

**목표:** Next.js 16 App Router + React 19 프로젝트에 Jest + RTL 기반 테스트 환경을 구성해 BE 단위/통합 테스트와 FE 컴포넌트/훅 테스트를 모두 실행할 수 있게 한다.

**아키텍처:** `next/jest`의 `createJestConfig`를 사용해 App Router 호환 처리(SWC 트랜스폼, 경로 별칭 자동 매핑)를 자동화한다. 기본 `testEnvironment`는 `node`(BE용)이며, FE 테스트 파일은 파일 상단 `/** @jest-environment jsdom */` 도큐블록으로 환경을 개별 지정한다.

**기술 스택:** Jest 29, @testing-library/react 16, @testing-library/jest-dom 6, next/jest (SWC 트랜스폼)

**스펙:** `docs/specs/2026-08-23-jest-setup-design.md`

## 전역 제약

- Next.js 16.3.2, React 19, TypeScript 5
- `moduleResolution: "bundler"` — next/jest의 SWC 트랜스폼으로 해소
- `jest.config.js` (CommonJS) 사용 — `jest.config.ts`는 Jest가 자체 config를 로드할 때 SWC 트랜스폼이 적용되기 전이라 ts-node 의존성이 추가로 필요함. `.js`가 신뢰성 높음
- BE 단위 테스트 위치: `__tests__/unit/services/`
- BE 통합 테스트 위치: `__tests__/integration/repositories/`
- FE 테스트 위치: 소스 파일 옆 코로케이션 (`*.test.tsx`)
- 테스트용 환경변수 파일: `.env.test.local` (gitignore 포함 — 로컬 전용)
- `@/*` 경로 별칭은 `next/jest`가 tsconfig.json에서 자동으로 읽음 — jest.config.js에 중복 설정 불필요

---

## 태스크 1: Jest 관련 패키지 설치

**파일:**
- 수정: `package.json` (devDependencies)

**인터페이스:**
- 생산: `node_modules`에 jest, jest-environment-jsdom, @testing-library/\* 설치 완료

---

- [ ] **스텝 1: 패키지 설치**

```bash
npm install --save-dev \
  jest \
  jest-environment-jsdom \
  "@testing-library/react" \
  "@testing-library/jest-dom" \
  "@testing-library/user-event" \
  "@types/jest"
```

- [ ] **스텝 2: 설치 확인**

실행: `cat package.json | grep -A 20 '"devDependencies"'`

예상: jest, jest-environment-jsdom, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, @types/jest 항목 확인

- [ ] **스텝 3: 커밋**

```bash
git add package.json package-lock.json
git commit -m "공통/chore: Jest + RTL 테스트 패키지 설치 closes #15"
```

---

## 태스크 2: Jest 설정 파일 작성

**파일:**
- 생성: `jest.config.js`
- 생성: `jest.setup.ts`
- 생성: `jest.env.setup.ts`

**인터페이스:**
- 소비: `next/jest` (createJestConfig), `@testing-library/jest-dom`, `dotenv`
- 생산: `npm test` 실행 가능한 Jest 설정

---

- [ ] **스텝 1: jest.config.js 작성**

`jest.config.js` (프로젝트 루트):

```js
const nextJest = require('next/jest')

const createJestConfig = nextJest({ dir: './' })

/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  setupFiles: ['<rootDir>/jest.env.setup.ts'],
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
}

module.exports = createJestConfig(config)
```

- [ ] **스텝 2: jest.setup.ts 작성**

`jest.setup.ts` (프로젝트 루트):

```ts
import '@testing-library/jest-dom'
```

- [ ] **스텝 3: jest.env.setup.ts 작성**

`jest.env.setup.ts` (프로젝트 루트):

```ts
import { config } from 'dotenv'

config({ path: '.env.test.local' })
```

- [ ] **스텝 4: 설정 파일 동작 확인**

실행: `npx jest --listTests`

예상: 오류 없이 실행됨 (현재는 테스트 파일 없으므로 빈 목록 출력)

오류 발생 시 체크리스트:
- `Cannot find module 'next/jest'` → next가 node_modules에 있는지 확인: `ls node_modules | grep next`
- `Cannot find module 'dotenv'` → `npm install --save-dev dotenv` (package.json에 이미 있으면 `npm install`)

- [ ] **스텝 5: 커밋**

```bash
git add jest.config.js jest.setup.ts jest.env.setup.ts
git commit -m "공통/chore: Jest 설정 파일 작성 (jest.config.js, jest.setup.ts)"
```

---

## 태스크 3: package.json scripts 추가 + .env.test.local 템플릿 생성

**파일:**
- 수정: `package.json` (scripts)
- 생성: `.env.test.local.example` (gitignore 제외 — 예시 파일)

**인터페이스:**
- 생산: `npm test`, `npm run test:unit`, `npm run test:integration`, `npm run test:fe` 명령어 사용 가능

---

- [ ] **스텝 1: package.json scripts 수정**

`package.json`의 `"scripts"` 섹션에 아래 항목 추가:

```json
"test": "jest --passWithNoTests --testPathPattern='(__tests__/unit|src)'",
"test:unit": "jest --passWithNoTests __tests__/unit",
"test:integration": "jest --passWithNoTests __tests__/integration",
"test:fe": "jest --passWithNoTests src",
"test:watch": "jest --watch"
```

- [ ] **스텝 2: .env.test.local.example 생성**

`.env.test.local.example` (프로젝트 루트):

```
# 이 파일을 복사해 .env.test.local을 생성하고 실제 값을 채운다.
# Supabase 테스트 전용 프로젝트 > Settings > Database > Connection string > Session mode

TEST_DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

- [ ] **스텝 3: .gitignore에 .env.test.local 포함 확인**

실행: `grep 'env' .gitignore`

예상: `.env*` 또는 `.env.test.local` 항목 확인. 없으면 `.gitignore`에 `.env.test.local` 추가

- [ ] **스텝 4: scripts 동작 확인**

실행: `npm test`

예상: `No tests found, exiting with code 0` (--passWithNoTests 적용)

- [ ] **스텝 5: 커밋**

```bash
git add package.json .env.test.local.example
git commit -m "공통/chore: npm test 스크립트 추가 및 테스트 환경변수 예시 파일 생성"
```

---

## 태스크 4: __tests__ 폴더 구조 생성 + 샘플 테스트로 환경 검증

**파일:**
- 생성: `__tests__/unit/services/.gitkeep`
- 생성: `__tests__/integration/repositories/.gitkeep`
- 생성(임시): `__tests__/unit/services/sample.test.ts`
- 생성(임시): `src/lib/utils.test.tsx`

**인터페이스:**
- 소비: `src/lib/utils.ts`의 `cn()` 함수 (BE 샘플), 인라인 React 컴포넌트 (FE 샘플)
- 생산: `npm test`, `npm run test:fe` 모두 PASS 확인

---

- [ ] **스텝 1: __tests__ 폴더 구조 생성**

```bash
mkdir -p __tests__/unit/services
mkdir -p __tests__/integration/repositories
touch __tests__/unit/services/.gitkeep
touch __tests__/integration/repositories/.gitkeep
```

- [ ] **스텝 2: BE 샘플 테스트 작성 (실패 확인용)**

`__tests__/unit/services/sample.test.ts`:

```ts
describe('테스트 환경 검증', () => {
  it('BE 단위 테스트 환경이 정상 동작한다', () => {
    expect(1 + 1).toBe(2)
  })

  it('@/* 경로 별칭이 동작한다', async () => {
    const { cn } = await import('@/lib/utils')
    expect(cn('foo', 'bar')).toBe('foo bar')
  })
})
```

- [ ] **스텝 3: BE 샘플 테스트 실행 확인**

실행: `npm run test:unit`

예상: PASS — 2개 테스트 통과

오류 발생 시 체크리스트:
- `Cannot find module '@/lib/utils'` → `jest.config.js`에서 `createJestConfig`가 올바르게 `@/*` 매핑을 읽는지 확인. `next/jest` 버전 확인: `npm list next`
- `SyntaxError: Cannot use import statement` → `next/jest`의 SWC 트랜스폼이 적용되지 않음. `jest.config.js`의 `createJestConfig` 호출 확인

- [ ] **스텝 4: FE 샘플 테스트 작성 (jsdom 도큐블록 확인)**

`src/lib/utils.test.tsx`:

```tsx
/**
 * @jest-environment jsdom
 */
import React from 'react'
import { render, screen } from '@testing-library/react'
import { cn } from '@/lib/utils'

describe('FE 테스트 환경 검증', () => {
  it('jsdom 환경에서 React 컴포넌트를 렌더링할 수 있다', () => {
    const TestComponent = (): React.JSX.Element => (
      <div data-testid="test">Hello</div>
    )
    render(<TestComponent />)
    expect(screen.getByTestId('test')).toBeInTheDocument()
  })

  it('cn 유틸리티가 정상 동작한다', () => {
    expect(cn('px-4', 'py-2')).toBe('px-4 py-2')
  })
})
```

- [ ] **스텝 5: FE 샘플 테스트 실행 확인**

실행: `npm run test:fe`

예상: PASS — 2개 테스트 통과

오류 발생 시 체크리스트:
- `toBeInTheDocument is not a function` → `jest.setup.ts`의 `import '@testing-library/jest-dom'`이 `setupFilesAfterEnv`에 등록됐는지 확인
- `document is not defined` → `/** @jest-environment jsdom */` 도큐블록이 파일 최상단에 있는지 확인

- [ ] **스텝 6: 전체 테스트 실행 확인**

실행: `npm test`

예상: PASS — unit + fe 테스트 모두 통과 (integration 제외)

- [ ] **스텝 7: 샘플 테스트 삭제**

```bash
rm __tests__/unit/services/sample.test.ts
rm src/lib/utils.test.tsx
```

- [ ] **스텝 8: 최종 커밋**

```bash
git add __tests__/ src/
git commit -m "공통/chore: 테스트 폴더 구조 생성 및 환경 검증 완료 closes #15"
```

---

## 셀프 리뷰 체크리스트

### 스펙 커버리지

| 스펙 항목 | 구현 태스크 |
|---------|-----------|
| Jest + RTL 설치 | 태스크 1 |
| jest.config.js 설정 | 태스크 2 |
| jest.setup.ts 설정 | 태스크 2 |
| tsconfig __tests__ 포함 확인 | 태스크 3 (tsconfig의 `**/*.ts`가 이미 커버 — 별도 수정 불필요 확인) |
| npm scripts 추가 | 태스크 3 |
| TEST_DATABASE_URL 문서화 | 태스크 3 (.env.test.local.example) |
| __tests__ 폴더 구조 | 태스크 4 |
| 샘플 테스트 동작 확인 | 태스크 4 |

### 완료 기준 대조

- [ ] `npm test` 실행 시 오류 없이 통과
- [ ] `npm run test:integration` 실행 시 TEST_DATABASE_URL 없으면 DB 연결 오류로 실패 (의도된 동작)
- [ ] FE 테스트에서 `toBeInTheDocument()` 사용 가능
- [ ] `@/*` 경로 별칭이 테스트 파일에서 정상 동작
