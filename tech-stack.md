# 기술 스택 정리 (바이브코딩 → Vercel 배포)

작성일: 2026-08-21

## 개요

AI 코딩 도구(바이브코딩)로 빠르게 개발하고, Vercel에 무료/저비용으로 배포하는 것을 목표로 한 스택입니다. 별도의 백엔드 서버 없이 Next.js 하나로 프론트엔드/백엔드를 모두 처리합니다.

**프로젝트**: 화장품 이커머스, 상품 약 100개, 상품당 썸네일 + 상세이미지 2종 이미지 운영

## 스택 요약

| 영역 | 선택 | 비고 |
|---|---|---|
| 프론트엔드 + 백엔드 | Next.js (App Router) | API Routes / Server Actions로 백엔드 로직 처리, 별도 서버 불필요 |
| UI / 스타일링 | Tailwind CSS + shadcn/ui | 컴포넌트 뼈대는 shadcn, 디자인 톤은 Tailwind 테마로 커스터마이징 |
| 디자인 연동 | Figma 원격 MCP 서버 | 무료 플랜에서도 사용 가능. 색상/타이포그래피/spacing 등 디자인 명세를 코드에 반영 |
| ORM | Drizzle | 경량 번들(~12KB), 콜드 스타트 유리, 별도 generate 단계 없음 |
| 데이터베이스 / 인증 | Supabase (Postgres + Auth) | DB, 로그인/회원가입 전용. 이미지 파일은 저장하지 않음 |
| 이미지 저장 | Cloudflare R2 | 10GB 무료, egress(다운로드) 비용 없음. 썸네일/상세이미지 최적화본 저장 |
| 이미지 처리 | sharp (Node 라이브러리) | 업로드 시 리사이즈 + WebP 변환 자동화 |
| 배포 | Vercel | Next.js 공식 배포처, 무료(Hobby) 티어로 시작 |

## 선택 이유

### Next.js 단일 스택 (Python 백엔드 없음)
AI 모델 API 단순 호출 수준 외에 Python이 꼭 필요한 로직(이미지/영상 처리, 데이터 분석 등)이 없다고 판단해, 프론트엔드와 백엔드를 Next.js 하나로 합쳤습니다. 서버 관리, 배포 파이프라인, 비용을 모두 줄일 수 있습니다.

### Tailwind + shadcn/ui
AI 코딩 도구들이 이 조합에 익숙해서 일관된 디자인 결과물을 빠르게 생성합니다. shadcn/ui는 npm 패키지가 아니라 컴포넌트 소스 코드를 CLI로 프로젝트에 직접 복사하는 방식이라 자유롭게 커스터마이징할 수 있습니다.

### Figma 원격 MCP 연동
- 원격(Remote) 서버: `mcp.figma.com`에 바로 연결, 모든 요금제(무료 포함)에서 사용 가능, 기능도 가장 폭넓음 (추천)
- 데스크톱(Desktop) 서버: 피그마 앱을 통해 로컬 실행, 유료 플랜의 Dev/Full 시트 필요, 기능 제한적 → 사용할 필요 없음

claude.ai 커넥터 설정에서 Figma를 연결하면 디자인 토큰(`get_variable_defs`)과 화면별 명세(`get_design_context`, 스크린샷)를 읽어와 Tailwind/shadcn 코드에 반영할 수 있습니다. 필요 시 `get_code_connect_map`으로 피그마 컴포넌트 ↔ 코드 컴포넌트 매핑도 설정 가능합니다.

### Drizzle vs Prisma
| 비교 항목 | Drizzle | Prisma |
|---|---|---|
| 번들 크기 | ~12KB (경량) | ~1.6MB |
| 서버리스 콜드 스타트 | 유리 | 상대적으로 불리 |
| 스키마 수정 후 | 별도 생성 단계 없음 | `prisma generate` 필요 |
| 학습 곡선 | SQL과 유사 | SQL 추상화로 진입장벽 낮음 |

바이브코딩에서는 쿼리를 AI가 대부분 생성해주므로 SQL 친숙도 차이보다 번들 크기·콜드 스타트 이점이 더 크다고 판단해 Drizzle을 선택했습니다.

### Supabase (DB/Auth 전용)
Postgres DB와 인증(로그인/회원가입)만 담당합니다. Supabase Storage는 무료 플랜 1GB 한도가 있고 초과 시 유료 플랜 전환이 필요해서, 이미지 저장 용도로는 쓰지 않기로 했습니다.

### 이미지 저장: Cloudflare R2
상품 100개 × (썸네일 + 상세이미지) 기준, 원본은 약 1.84GB지만 웹 노출용으로 리사이즈 + WebP 변환하면 실제 저장 용량은 수십~수백 MB 수준으로 줄어듭니다. R2는 스토리지 10GB까지 무료이고 다운로드(egress) 비용이 없어서, 상품 이미지처럼 자주 조회되는 콘텐츠를 저장하기에 Supabase Storage보다 유리합니다. S3 호환 API라 관련 라이브러리를 그대로 사용할 수 있습니다.

**처리 흐름**: 어드민에서 원본 이미지 업로드 → 서버에서 `sharp`로 썸네일(짧은 변 400~600px)/상세이미지(가로 800~1200px) 두 가지 크기로 리사이즈 + WebP 변환 → R2에 저장 → 프론트엔드는 Next.js `<Image>` 컴포넌트로 화면 크기별 추가 최적화. 고해상도 원본 촬영 파일은 R2에 두지 않고 별도 백업(로컬/드라이브 등)으로 보관합니다.

## 다음 단계 체크리스트

- [ ] Next.js 프로젝트 생성 (`create-next-app`)
- [ ] Tailwind CSS + shadcn/ui 설치 및 초기 세팅
- [ ] Supabase 프로젝트 생성 (DB + Auth)
- [ ] Drizzle 스키마 작성 및 Supabase Postgres 연결
- [ ] Cloudflare R2 버킷 생성 및 API 키 발급
- [ ] 이미지 업로드 파이프라인 구현 (sharp 리사이즈/WebP 변환 → R2 업로드)
- [ ] claude.ai 커넥터 설정에서 Figma 연결 (원격 MCP)
- [ ] GitHub 리포지토리 생성 및 코드 푸시
- [ ] Vercel에 리포지토리 연결, 환경 변수(Supabase, R2 키 등) 설정 후 배포
