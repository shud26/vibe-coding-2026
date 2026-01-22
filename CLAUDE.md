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
- 블로그 글: Day 1, 2, 3, 4, 5 작성 완료

### 2. vibe-coding-2026 (메인 레포)
- 경로: `/Users/hun/vibe-coding-2026`
- GitHub: https://github.com/shud26/vibe-coding-2026
- 1년 로드맵, 학습 기록, 프로젝트 코드

### 3. crypto-portfolio
- 경로: `/Users/hun/crypto-portfolio`
- GitHub: https://github.com/shud26/crypto-portfolio
- BTC/ETH/SOL 가격 트래커 (GitHub Actions 매 시간 업데이트)

### 4. 포트폴리오 웹사이트 (구버전)
- 경로: `/Users/hun/shud26.github.io`
- URL: https://shud26.github.io
- 간단한 HTML/CSS 사이트

---

## 만든 툴들

| 툴 | 위치 | 설명 |
|---|------|------|
| **Cross-DEX 펀딩비 차익거래 봇** | `vibe-coding-2026/projects/funding-arbitrage/funding_arb.py` | Hyperliquid vs Binance 스프레드 모니터링 |
| **Todo + Calendar CLI** | `vibe-coding-2026/projects/funding-arbitrage/todo_calendar.py` | 할 일 + Google Calendar 연동 |
| **Morning Briefing Bot** | `vibe-coding-2026/projects/funding-arbitrage/morning_briefing.py` | 매일 아침 8시 오늘 일정+할일 텔레그램 알림 |
| 멀티 DEX 펀딩비 트래커 | `vibe-coding-2026/projects/funding-tracker/multi_dex_funding.py` | 3개 DEX 펀딩비 + 차익거래 알림 |
| GitHub Actions 알림 | `vibe-coding-2026/.github/workflows/funding-alert.yml.disabled` | 1시간마다 자동 펀딩비 체크 (비활성화됨) |
| 단일 펀딩비 트래커 | `vibe-coding-2026/projects/funding-tracker/funding_tracker.py` | Hyperliquid 전용 |
| BTC 알림봇 | `claude-code-achievements/btc_alert.py` | 만 달러 단위 돌파 알림 |
| 업비트 상장 알림 봇 | `vibe-coding-2026/projects/upbit-listing-alert/upbit_listing.py` | 마켓 리스트 방식 (비활성화됨) |
| **실시간 대시보드** | `shud-portfolio/src/app/dashboard/` | 9개 코인, 차익거래 기회 표시 |
| **Todo List + Calendar** | `shud-portfolio/src/app/todo/` | PIN 잠금 + 텔레그램 + Google Calendar |
| **Paper Trading** | `shud-portfolio/src/app/trade/` | 가상 $10,000으로 연습 |

---

## shud-portfolio 사이트 기능

### Dashboard (/dashboard)
- 9개 코인: BTC, ETH, SOL, DOGE, AVAX, ARB, SUI, LINK, XRP
- 3개 DEX: Hyperliquid, Pacifica, Variational
- 차익거래 기회 TOP 3 표시
- 예상 일일 수익률 계산
- **김치 프리미엄 모니터링** (CoinGecko API, KRW vs USD, 실시간 환율)
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
| Variational | Arbitrum | `omni-client-api.prod.ap-northeast-1.variational.io` | ⚠️ 읽기만 가능 (Trading API 개발 중) |
| Nado | Ink (Kraken L2) | 확인 필요 | 미연동 |
| Extended | Starknet | 확인 필요 | 미연동 |

**상세 DEX 정보:** `vibe-coding-2026/ideas/perp-dex-info.md`

---

## 설정 정보

### Telegram Bot
- Token: `7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI`
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

# 포트폴리오 사이트 로컬 실행
cd /Users/hun/shud-portfolio
npm run dev
```

---

## Vercel 배포 ✅ 완료

- shud-portfolio 레포 연결됨
- git push 하면 자동 배포!
- URL: https://shud26.vercel.app
- ⚠️ Google Calendar 환경변수 설정 필요 (Vercel 대시보드에서)

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
- [x] 블로그 글 작성 (Day 1, 2, 3, 4 완료) ✅
- [x] 대시보드 실시간 데이터 연동 ✅
- [x] Todo List + 텔레그램 알림 ✅
- [x] Google Calendar 연동 ✅
- [x] 펀딩비 차익거래 모니터링 봇 ✅
- [x] Morning Briefing Bot (매일 아침 8시 자동 알림) ✅
- [x] 김치 프리미엄 모니터링 (대시보드에 추가) ✅
- [ ] 펀딩비 차익거래 실제 테스트 (소액)
- [ ] 자동 진입/청산 기능 추가
- [ ] Bybit 거래소 추가
- [x] 업비트 신규 상장 알림 (마켓 리스트 방식, 공지 API 없어서 실용성 낮음)
- [ ] DEX 신규 페어 알림
- [ ] 퍼프덱 신규 상장 스나이핑 (공지 API 필요)

---

## 세션 종료 시 할 일

⚠️ **중요: 개발 끝나기 전에 물어보기!**
```
"오늘도 블로그 글 쓰셔야 해요! Day X 쓸까요?"
```

블로그 위치: `/Users/hun/shud-portfolio/src/app/blog/`
- Day 1: 2026-01-17 (Claude Code 설치, BTC 가격 조회, 텔레그램 봇, GitHub 연동)
- Day 2: 2026-01-18 (포트폴리오 사이트, 멀티 DEX 트래커, GitHub Actions, Vercel 배포)
- Day 3: 2026-01-19 (대시보드 풀 업그레이드, Todo List + 텔레그램, React Hooks 버그 수정)
- Day 4: 2026-01-20 (Cross-DEX 차익거래 봇, Google Calendar 연동, Todo 업그레이드)
- Day 5: 2026-01-21 (Morning Briefing Bot, 김치 프리미엄 모니터링)
- Day 6: 2026-01-23 (업비트 상장 알림 시도, API 리서치, 한계점 발견)

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
- paradexbot 폴더에 추가 코드 있음
- 학습 기록: `vibe-coding-2026/logs/`
- DEX 정보: `vibe-coding-2026/ideas/perp-dex-info.md`

---
*마지막 업데이트: 2026-01-23*
