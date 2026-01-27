# Claude Context

## 나는 누구?
- GitHub: shud26
- 코딩 입문자, 바이브코딩으로 성장 중
- 목표: 돈 버는 크립토 툴 만들기

---

## 진행 중인 프로젝트

### 1. shud-portfolio (Vercel 사이트) ✅ 배포 완료
- 경로: `/Users/hun/shud-portfolio`
- GitHub: https://github.com/shud26/shud-portfolio
- 배포: https://shud26.vercel.app
- 기술: Next.js, TypeScript, Tailwind CSS
- 페이지: 메인, Projects, Blog, Dashboard, Todo, Trade
- 블로그 글: Day 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 작성 완료

### 2. vibe-coding-2026 (메인 레포)
- 경로: `/Users/hun/vibe-coding-2026`
- GitHub: https://github.com/shud26/vibe-coding-2026
- 1년 로드맵, 학습 기록, 프로젝트 코드

### 3. shud-onepage (tftchess.com) ✅ NEW!
- 경로: `/Users/hun/tftchess`
- GitHub: https://github.com/shud26/shud-onepage
- 배포: https://tftchess.com
- 기술: Next.js 16 + TypeScript + Tailwind CSS + Supabase
- 기능: 원페이지 크립토 대시보드
  - 에어드랍 트래커 (태스크별 비용 관리)
  - 코인 리서치 노트 (풀스크린 상세보기)
  - 캘린더 + 이벤트 메모
  - 할 일 목록
  - 김치 프리미엄 & 차익거래 기회
  - 고래 지갑 추적 + 활동 분석
  - **Whale Alert** (5+ ETH / $50K+ 토큰 이동 텔레그램 알림, 매일 오전 8시 자동 체크)
  - **개발 블로그** (/blog, /blog/[slug]) - Day 1~11 글, PIN 로그인 후 추가/수정/삭제
  - PIN 로그인 (1507)
- DB: Supabase (airdrops, airdrop_tasks, todos, events, research, whale_wallets, whale_alerts, blog_posts)

### 4. Variational Delta Neutral Bot ✅ 실거래 완료
- 경로: `/Users/hun/vibe-coding-2026/projects/variational-delta-neutral`
- GitHub: https://github.com/shud26/variational-delta-neutral
- 기술: Python3, curl_cffi (Cloudflare 우회), eth_account, web3.py
- 체인: Arbitrum One (USDC)
- 기능:
  - 2계정 델타뉴트럴 포인트 파밍 (A1 매수 + A2 매도 → 청산)
  - SIWE 서명 로그인 → JWT + vr-token 인증
  - 지정가/시장가 주문, 포지션/잔액 조회
  - 텔레그램 알림 (사이클 완료, 잔액 부족, 수익 발생)
  - 잔액 모니터링 ($300 이하 시 입금 알림)
  - 자동 입출금 코드 구현 (Cloudflare 차단으로 대기 중)
  - Arbitrum 지갑 USDC 잔액 조회 (web3.py)
- 파일:
  - `variational_client.py` - API 클라이언트 (로그인, 주문, 잔액, 입출금)
  - `variational_bot.py` - 메인 봇 (델타뉴트럴 사이클, 자동 반복, 잔액 관리)
  - `variational_app.py` - 데스크톱 GUI (tkinter)
- 컨트랙트:
  - Oracle: `0x84BE56470d45b7f6629A66A219a38681F6BA6172`
  - USDC (Arbitrum): `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`
  - A1 Settlement Pool: `0xaB9Ef61C5d4c963ca4bD361577051B9b0E14a5c9`
  - A2 Settlement Pool: `0x291B7091FD6A3bA497588fB8Abca36d13c090ba0`

### 5. Triangle Dice Mini App
- 경로: `/Users/hun/vibe-coding-2026/triangle-dice-miniapp`
- GitHub: https://github.com/shud26/triangle-dice-miniapp
- 배포: https://triangle-dice-miniapp.vercel.app
- 기술: Vite + React + TypeScript + wagmi
- 체인: Base Sepolia (테스트넷)
- 기능: 1v1 USDC 베팅 주사위 게임
- 상태: 웹 브라우저 호환성 수정 완료 ✅

### 6. crypto-portfolio
- 경로: `/Users/hun/crypto-portfolio`
- GitHub: https://github.com/shud26/crypto-portfolio
- BTC/ETH/SOL 가격 트래커 (GitHub Actions 매 시간 업데이트)

### 7. 포트폴리오 웹사이트 (구버전)
- 경로: `/Users/hun/shud26.github.io`
- URL: https://shud26.github.io
- 간단한 HTML/CSS 사이트

---

## 만든 툴들

| 툴 | 위치 | 설명 |
|---|------|------|
| **shud-onepage** | `tftchess/` | 원페이지 크립토 대시보드 (에어드랍, 리서치, 캘린더, 블로그) |
| **개발 블로그** | `tftchess/src/app/blog/` | Day 1~11 블로그, Supabase blog_posts, PIN 관리 |
| **Whale Alert** | `tftchess/src/lib/whale-checker.ts` | 고래 지갑 5+ ETH / $50K+ 토큰 이동 텔레그램 알림 |
| **Triangle Dice Mini App** | `vibe-coding-2026/triangle-dice-miniapp` | Base Mini App - 1v1 USDC 베팅 게임 |
| **Variational Delta Neutral Bot** | `vibe-coding-2026/projects/variational-delta-neutral/` | 2계정 델타뉴트럴 포인트 파밍 (Arbitrum) |
| **Cross-DEX 펀딩비 차익거래 봇** | `vibe-coding-2026/projects/funding-arbitrage/funding_arb.py` | Hyperliquid vs Binance 스프레드 모니터링 |
| **Todo + Calendar CLI** | `vibe-coding-2026/projects/funding-arbitrage/todo_calendar.py` | 할 일 + Google Calendar 연동 |
| **Morning Briefing Bot** | `vibe-coding-2026/projects/funding-arbitrage/morning_briefing.py` | 매일 아침 8시 오늘 일정+할일 텔레그램 알림 |
| 멀티 DEX 펀딩비 트래커 | `vibe-coding-2026/projects/funding-tracker/multi_dex_funding.py` | 3개 DEX 펀딩비 + 차익거래 알림 |
| GitHub Actions 알림 | `vibe-coding-2026/.github/workflows/funding-alert.yml.disabled` | 1시간마다 자동 펀딩비 체크 (비활성화됨) |
| 단일 펀딩비 트래커 | `vibe-coding-2026/projects/funding-tracker/funding_tracker.py` | Hyperliquid 전용 |
| BTC 알림봇 | `claude-code-achievements/btc_alert.py` | 만 달러 단위 돌파 알림 |
| 업비트 상장 알림 봇 | `vibe-coding-2026/projects/upbit-listing-alert/upbit_listing.py` | 마켓 리스트 방식 (비활성화됨) |
| **CEX/DEX 가격 갭 모니터링** | `vibe-coding-2026/projects/price-gap-monitor/price_gap.py` | 5개 거래소 가격 비교 + 텔레그램 알림 |
| **실시간 대시보드** | `shud-portfolio/src/app/dashboard/` | 9개 코인, 차익거래 + 가격 갭 모니터링 |
| **Todo List + Calendar** | `shud-portfolio/src/app/todo/` | PIN 잠금 + 텔레그램 + Google Calendar |
| **Paper Trading** | `shud-portfolio/src/app/trade/` | 가상 $10,000으로 연습 |

---

## Triangle Dice Mini App 상세

### 개요 (Overview)
- **1v1 베팅 게임**: 두 플레이어가 USDC를 걸고 주사위 게임
- **삼각형 완성**: 점들을 연결해 삼각형을 만들면 점수 획득
- **스마트 컨트랙트**: 에스크로 방식으로 안전한 베팅

### 기술 스택 (Tech Stack)
- Frontend: Vite + React 19 + TypeScript
- Web3: wagmi 2.x + viem + @coinbase/onchainkit
- Mini App SDK: @farcaster/miniapp-sdk
- Chain: Base Sepolia Testnet

### 컨트랙트 주소 (Contract Addresses)
- MockUSDC: `0x2aC28e4754a9Eeae143399fC1B0B1F9bBe9E2CC3`
- Escrow: `0x0e6Bb9F887B3ca03d942558FaB935701C5A44f21`

### 주요 파일 (Key Files)
```
triangle-dice-miniapp/
├── src/
│   ├── main.tsx          # MiniKitProvider 설정
│   ├── App.tsx           # 메인 앱 + SDK ready() 호출
│   ├── config.ts         # wagmi + 체인 설정
│   ├── minikit.config.ts # Mini App 메타데이터
│   ├── pages/
│   │   ├── Lobby.tsx     # 매치 생성/참가
│   │   ├── Board.tsx     # 게임 보드
│   │   └── Result.tsx    # 결과 화면
│   └── components/
│       └── WalletConnect.tsx  # 지갑 연결
├── public/
│   ├── .well-known/
│   │   └── farcaster.json    # Mini App manifest
│   └── assets/
│       ├── icon.png      # 앱 아이콘 (200x200)
│       ├── splash.png    # 스플래시 (400x400)
│       └── preview.png   # 프리뷰 (1200x630)
└── index.html            # base:app_id 메타태그
```

### Mini App 등록 절차 (Registration Process)
1. base.dev 접속 (VPN 필요 - 한국 차단)
2. App URL 입력 → 메타태그로 소유권 인증
3. 지갑 서명 → Account Association 생성
4. farcaster.json 업데이트 (header, payload, signature)
5. primaryCategory, tags 등 메타데이터 추가

### 현재 상태 (Current Status)
- ✅ Vercel 배포 완료
- ✅ 스마트 컨트랙트 배포 (Base Sepolia)
- ✅ OnchainKit + MiniKit 통합
- ✅ Account Association 완료
- ✅ 메타데이터 설정 완료
- ⏳ Ready call 디버깅 중
- ⏳ Base App 검색 인덱싱 대기

---

## shud-portfolio 사이트 기능

### Dashboard (/dashboard)
- 9개 코인: BTC, ETH, SOL, DOGE, AVAX, ARB, SUI, LINK, XRP
- 3개 DEX: Hyperliquid, Pacifica, Variational
- 차익거래 기회 TOP 3 표시
- 예상 일일 수익률 계산
- **김치 프리미엄 모니터링** (CoinGecko API, KRW vs USD, 실시간 환율)
- **CEX/DEX 가격 갭 모니터링** (Binance, Bybit, OKX, Bitget, Hyperliquid)
  - Hyperliquid 전체 코인 (500개+) 모니터링
  - 1% 이상 갭만 표시 + 텔레그램 알림
- 60초 자동 새로고침

### Todo List (/todo) - 풀 업그레이드!
- PIN 잠금: `1507`
- **날짜/시간/데드라인 설정**
- **Google Calendar 자동 연동**
- 텔레그램 알림 (추가/완료 시)
- 데드라인 색상 표시 (노란색: 임박, 빨간색: 지남)
- 필터: 전체, 오늘, 예정, 진행 중, 완료됨

### Trade (/trade)
- 가상 $10,000 잔액
- 롱/숏 포지션
- 1-10배 레버리지
- 실시간 PnL 계산
- 거래 기록 및 승률

---

## 지원 DEX 정보

| DEX | 체인 | API | 상태 |
|-----|------|-----|------|
| Hyperliquid | 자체 L1 | `api.hyperliquid.xyz` | ✅ 연동 |
| Binance | - | `fapi.binance.com` | ✅ 연동 (차익거래용) |
| Pacifica | Solana | `api.pacifica.fi` | ✅ 연동 |
| Variational | Arbitrum | `omni.variational.io` (curl_cffi 필요) | ✅ 거래 연동 완료 (입출금 API는 CF 차단) |
| Nado | Ink (Kraken L2) | 확인 필요 | 미연동 |
| Extended | Starknet | 확인 필요 | 미연동 |

**상세 DEX 정보:** `vibe-coding-2026/ideas/perp-dex-info.md`

---

## 설정 정보

### Telegram Bot
- Chat ID: `6329588659`

### GitHub CLI
- 경로: `/Users/hun/.local/bin/gh`
- 계정: shud26

### GitHub Secrets (vibe-coding-2026)
- TELEGRAM_TOKEN: 설정됨
- TELEGRAM_CHAT_ID: 설정됨
- GOOGLE_TOKEN_JSON: 설정됨
- GOOGLE_CREDENTIALS_JSON: 설정됨

### Google Calendar API
- credentials.json: `/Users/hun/vibe-coding-2026/projects/funding-arbitrage/credentials.json`
- token.json: `/Users/hun/vibe-coding-2026/projects/funding-arbitrage/token.json`
- 환경변수 (shud-portfolio): `.env.local`에 저장
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - GOOGLE_REFRESH_TOKEN

### Todo PIN
- PIN: `1507`

---

## 실행 명령어

```bash
# shud-onepage 로컬 실행
cd /Users/hun/tftchess
npm run dev

# Triangle Dice Mini App 로컬 실행
cd /Users/hun/vibe-coding-2026/triangle-dice-miniapp
npm run dev

# Cross-DEX 펀딩비 차익거래 봇 (한 번)
cd /Users/hun/vibe-coding-2026/projects/funding-arbitrage
python3 funding_arb.py --once

# 30분마다 반복 실행
python3 funding_arb.py

# Todo + Calendar CLI
python3 todo_calendar.py add "할일" --date tomorrow
python3 todo_calendar.py list
python3 todo_calendar.py done 1

# Morning Briefing (수동 실행)
python3 morning_briefing.py          # 바로 전송
python3 morning_briefing.py --test   # 테스트 (전송 안함)

# Variational Delta Neutral Bot
cd /Users/hun/vibe-coding-2026/projects/variational-delta-neutral
python3 variational_bot.py --once              # 1사이클 실행
python3 variational_bot.py --once --dry-run    # 시뮬레이션
python3 variational_bot.py --accounts 2        # 자동 반복
python3 variational_bot.py --status            # 상태 확인
python3 variational_bot.py --close-all         # 긴급 청산
python3 variational_bot.py --balance           # 잔액 관리

# 포트폴리오 사이트 로컬 실행
cd /Users/hun/shud-portfolio
npm run dev
```

---

## Vercel 배포 ✅ 완료

- shud-portfolio 레포 연결됨
- triangle-dice-miniapp 레포 연결됨
- shud-onepage 레포 연결됨 (tftchess.com 도메인)
- git push 하면 자동 배포!
- URLs:
  - https://shud26.vercel.app
  - https://triangle-dice-miniapp.vercel.app
  - https://tftchess.com

---

## 사이트 수정 방법

```
"사이트 ㅇㅇ 수정해줘" 라고 말하면:
1. /Users/hun/shud-portfolio 파일 수정
2. git push
3. Vercel 자동 배포
4. 완료!
```

---

## 다음에 할 것
- [x] Vercel 배포 완료하기 ✅
- [x] 블로그 글 작성 (Day 1-8 완료) ✅
- [x] 대시보드 실시간 데이터 연동 ✅
- [x] Todo List + 텔레그램 알림 ✅
- [x] Google Calendar 연동 ✅
- [x] 펀딩비 차익거래 모니터링 봇 ✅
- [x] Morning Briefing Bot (매일 아침 8시 자동 알림) ✅
- [x] 김치 프리미엄 모니터링 (대시보드에 추가) ✅
- [x] Triangle Dice Mini App 개발 ✅
- [x] Base Mini App 등록 시작 ✅
- [x] shud-onepage 사이트 생성 (tftchess.com) ✅
- [x] Whale Alert 기능 (고래 지갑 이동 텔레그램 알림) ✅
- [x] tftchess.com 블로그 기능 추가 + Day 1~10 이전 ✅
- [x] Variational Delta Neutral Bot 개발 + 실거래 성공 ✅
- [x] Variational API 역공학 (로그인, 주문, 시세, 잔액) ✅
- [x] 잔액 모니터링 + 텔레그램 알림 ✅
- [ ] Variational 자동 입출금 (API 오픈 대기)
- [ ] shud-onepage 이미지 첨부 기능
- [ ] 블로그 SEO 메타태그 (og:title 등)
- [ ] shud-onepage 광고 추가 (AdSense)
- [ ] Triangle Dice Ready call 문제 해결
- [ ] Base App에서 검색 가능하게 만들기
- [ ] 메인넷 배포 (실제 USDC 사용)
- [ ] 펀딩비 차익거래 실제 테스트 (소액)
- [ ] 자동 진입/청산 기능 추가

---

## 세션 종료 시 할 일

⚠️ **중요: 개발 끝나기 전에 물어보기!**
```
"오늘도 블로그 글 쓰셔야 해요! Day X 쓸까요?"
```

블로그 위치: `tftchess.com/blog` (Supabase blog_posts 테이블)
- 기존 위치: `/Users/hun/shud-portfolio/src/app/blog/` (Day 1~10, 이전 완료)
- Day 1: 2026-01-17 (Claude Code 설치, BTC 가격 조회, 텔레그램 봇, GitHub 연동)
- Day 2: 2026-01-18 (포트폴리오 사이트, 멀티 DEX 트래커, GitHub Actions, Vercel 배포)
- Day 3: 2026-01-19 (대시보드 풀 업그레이드, Todo List + 텔레그램, React Hooks 버그 수정)
- Day 4: 2026-01-20 (Cross-DEX 차익거래 봇, Google Calendar 연동, Todo 업그레이드)
- Day 5: 2026-01-21 (Morning Briefing Bot, 김치 프리미엄 모니터링)
- Day 6: 2026-01-23 (업비트 상장 알림 시도, API 리서치, 한계점 발견)
- Day 7: 2026-01-23 (CEX/DEX 가격 갭 모니터링, 대시보드 업그레이드)
- Day 8: 2026-01-24 (Triangle Dice → Base Mini App 변환, Account Association 완료)
- Day 9: 2026-01-24 (shud-onepage 사이트 생성, Supabase 연동, tftchess.com 배포)
- Day 10: 2026-01-26 (Triangle Dice 웹 호환성 수정, Clawdbot 리서치, 구형 맥 서버 시도)
- Day 11: 2026-01-27 (tftchess.com 블로그 기능 추가, Day 1~10 이전, 홈페이지 배너, Variational Delta Neutral Bot 실거래 성공, 자동 입출금 구현 시도)

---

## 배운 것들 (Day 11)

### tftchess.com 블로그 기능
- Next.js App Router 동적 라우팅 ([slug] 폴더)
- dangerouslySetInnerHTML로 HTML 본문 렌더링
- PostgreSQL TEXT[] (배열 타입)으로 태그 저장
- Supabase upsert로 중복 없이 데이터 삽입
- .blog-content CSS 클래스로 HTML 본문 스타일링
- 마이그레이션 스크립트 (npx tsx migrate_blog.ts)

### JSX → HTML 변환
- className → class
- {" "} → 공백
- JSX 표현식 → 순수 HTML
- 파란 테마 → 오렌지 테마 (#FF5C00)

### 블로그 구조
- /blog → 목록 (Supabase에서 조회, 최신순)
- /blog/[slug] → 개별 글 (dangerouslySetInnerHTML)
- 홈페이지 → 최신 3개 글 프리뷰 카드
- PIN 로그인 후 CRUD (추가/수정/삭제)

### Variational DEX API 역공학
- SIWE (Sign-In with Ethereum) 인증: plain text 메시지 서명 → JWT + vr-token 쿠키
- curl_cffi로 Cloudflare TLS fingerprint 우회 (Chrome impersonation)
- instrument 형식: `{"instrument_type": "perpetual_future", "underlying": "BTC", "funding_interval_s": 3600, "settlement_asset": "USDC"}`
- 주문: `rfq_id`로 추적, `order_type: "limit"` + `limit_price` 필요
- 시장가: `quote_id`만으로 주문
- 잔액: `/api/settlement_pools/details` → `data["balance"]`
- Cloudflare 429 rate limit → 재시도 로직 (exponential backoff)

### 델타뉴트럴 전략 실전
- A1 매수 + A2 매도 → 같은 가격에 양방향 주문
- 체결 후 역방향 주문으로 청산
- 가격 위험 없이 거래량 발생 → 포인트 파밍
- 부분 체결 시 시장가 청산으로 손실 최소화

### Variational 자동 입출금 (미완)
- 스마트 컨트랙트 `depositUSDC`/`withdrawUSDC`는 PROVIDER_ROLE 필요 (직접 호출 불가)
- 입금 흐름: ERC-2612 permit 서명 → API → 백엔드가 온체인 실행
- API 엔드포인트 찾음: `/api/transfers/permit/template`, `/api/transfers/new`
- 하지만 Cloudflare JavaScript 챌린지로 차단됨
- Oracle 컨트랙트의 `getPool(uint128)` 함수로 pool 주소 조회 가능
- web3.py로 Arbitrum 온체인 USDC 잔액 조회 구현

### Variational 컨트랙트 구조
- Oracle 컨트랙트: 모든 입출금 트랜잭션 실행 (PROVIDER_ROLE 필요)
- Settlement Pool Factory: 사용자별 풀 생성
- Settlement Pool: 사용자-OLP 쌍별 독립 풀 (EIP-1167 minimal proxy)
- ERC-2612 permit: USDC가 네이티브 지원, 가스비 없이 승인 가능

---

## 배운 것들 (Day 10)

### Triangle Dice 웹 브라우저 호환성
- Mini App SDK는 일반 브라우저에서 작동 안 함
- MiniKitProvider 제거 필요
- useMiniKit, useIsInMiniApp 훅 제거
- wagmi 훅만 사용하면 웹에서도 작동
- 컨트랙트 주소 하드코딩 (Vercel env 없어서)

### Clawdbot (개인 AI 비서)
- Claude 기반 오픈소스 개인 비서
- 텔레그램/디스코드 등으로 접속
- 이메일, 캘린더, 브라우저 자동화, 터미널 실행 가능
- proactive 알림 가능 (먼저 연락함)
- 보안 주의: 파일/터미널 접근 권한 있음
- 크립토 지갑 있는 PC에 설치 비추천
- GitHub: https://github.com/clawdbot/clawdbot

### 구형 맥 서버 시도
- 24시간 크립토 봇 서버로 쓰려고 함
- OS 버전 너무 낮아서 실패
- 대안 필요: 클라우드 서버, 라즈베리 파이 등

---

## 배운 것들 (Day 9)

### Cloudflare Pages vs Vercel
- Cloudflare Pages는 Next.js 15.5.2까지만 지원
- Next.js 16 사용하려면 Vercel 사용
- @cloudflare/next-on-pages 패키지의 peer dependency 제한

### Supabase 연동
- PostgreSQL 기반 무료 데이터베이스
- RLS(Row Level Security) 기본 활성화
- 개인용은 `ALTER TABLE xxx DISABLE ROW LEVEL SECURITY;`
- anon key는 공개해도 안전 (RLS로 보호됨)

### Vercel 환경변수 문제
- NEXT_PUBLIC_ 접두사 필요 (클라이언트 노출용)
- 환경변수가 undefined면 "Invalid value" 에러 발생
- 해결: 코드에 직접 하드코딩 (anon key만)

### CSS 텍스트 줄바꿈
- `white-space: pre-wrap` - 줄바꿈 유지
- `word-wrap: break-word` - 긴 단어 줄바꿈
- `max-w-3xl` - 적당한 폭에서 자동 줄바꿈

---

## 배운 것들 (Day 8)

### Base Mini App 개발
- Base Mini App = Farcaster Mini App과 호환
- Coinbase Wallet(Base App)에서 실행 가능한 경량 앱
- farcaster.json manifest 파일 필수

### Mini App 등록 과정
1. `/.well-known/farcaster.json` 파일 생성
2. base.dev에서 소유권 인증 (메타태그 방식)
3. 지갑 서명으로 Account Association 생성
4. manifest에 header, payload, signature 추가
5. primaryCategory, tags 등 메타데이터 필수

### 한국에서 base.dev 접속
- Coinbase 서비스가 한국에서 제한됨
- VPN (미국) 사용하면 접속 가능
- Base App 자체는 한국에서 사용 가능 (170개국 지원)

### OnchainKit vs Farcaster SDK
- OnchainKit: Coinbase에서 만든 React 컴포넌트 라이브러리
- @farcaster/miniapp-sdk: Mini App 전용 SDK
- sdk.actions.ready() 호출로 앱 로딩 완료 신호

### wagmi 버전 호환성
- OnchainKit 1.x는 wagmi 2.x 필요
- wagmi 3.x와 호환 안 됨
- 다운그레이드 필요: `npm install wagmi@^2.16`

---

## 배운 것들 (Day 7)

### CEX/DEX 가격 갭 모니터링
- 같은 코인이라도 거래소마다 가격이 다름
- 이 차이를 이용한 차익거래 가능
- 단, 수수료, 슬리피지, 전송 시간 고려 필요

### 거래소 API 연동
- Binance: `fapi.binance.com/fapi/v1/ticker/price`
- Bybit: `api.bybit.com/v5/market/tickers`
- OKX: `www.okx.com/api/v5/market/tickers`
- Bitget: `api.bitget.com/api/v2/mix/market/tickers`
- Hyperliquid: `api.hyperliquid.xyz/info` (POST)

### False Positive 필터링
- 같은 심볼이라도 다른 토큰일 수 있음 (NTRN 등)
- 15% 이상 갭은 제외 (다른 토큰일 가능성)
- 최소 3개 거래소에서 가격 있어야 신뢰도 높음

---

## 배운 것들 (Day 6)

### 업비트 공지 API 현실
- 업비트 공지사항 API는 **공식적으로 제공 안 함**
- 예전에는 `api-manager.upbit.com/api/v1/notices` 작동했으나 현재 막힘
- 기존 텔레그램 봇들은 Selenium 스크래핑 또는 예전 API 사용 추정
- 뉴스 RSS (코인니스, 크립토패닉 등)도 대부분 막힘

### 마켓 리스트 방식의 한계
- `api.upbit.com/v1/market/all` API는 작동함
- 새 코인이 마켓에 추가되면 감지 가능
- **문제**: 공지 → 마켓 오픈까지 시간차 있음
- 스나이핑 목적으로는 부적합 (공지 시점에 알아야 함)

### 크립토 알림봇의 현실
- 대부분의 거래소는 공지 API를 공개하지 않음
- 빠른 알림을 위해서는 복잡한 스크래핑 필요
- 또는 유료 뉴스 API 서비스 사용 필요

---

## 배운 것들 (Day 5)

### Vercel 서버 지역 제한
- 업비트 API는 한국 IP만 허용
- Vercel 서버는 미국에 있어서 업비트 API 호출 실패
- 해결: CoinGecko API 사용 (전 세계에서 작동)

### CoinGecko API
- 무료로 암호화폐 가격 조회 가능
- KRW, USD 등 여러 통화 동시 조회
- `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=krw,usd`

### GitHub Actions cron
- 매일 특정 시간에 자동 실행
- `cron: '0 23 * * *'` = 매일 UTC 23시 = 한국시간 08시

---

## 배운 것들 (Day 4)

### 펀딩비 차익거래
- Hyperliquid와 Binance의 펀딩비 차이를 이용
- 한쪽 롱, 한쪽 숏 = 델타뉴트럴 (가격 위험 없음)
- 8시간마다 펀딩비 차이만큼 수익
- 스프레드 0.01% = 연 10.95% 수익률

### Google OAuth 2.0
- Google Cloud Console에서 프로젝트 생성
- OAuth 동의 화면 설정 + 테스트 사용자 추가
- credentials.json 다운로드
- 처음 실행 시 브라우저에서 인증
- refresh_token으로 자동 갱신

### GitHub 시크릿 보호
- 하드코딩된 API 키는 push 차단됨
- 환경변수로 관리 (.env.local)
- Vercel에서도 환경변수 설정 필요

---

## 참고
- **김테크 (본업)**: `/Users/hun/kimtech/CLAUDE.md` - 기술교사 프로젝트 별도 관리
- paradexbot 폴더에 추가 코드 있음
- 학습 기록: `vibe-coding-2026/logs/`
- DEX 정보: `vibe-coding-2026/ideas/perp-dex-info.md`

---
*마지막 업데이트: 2026-01-27*
