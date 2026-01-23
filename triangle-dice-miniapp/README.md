# Triangle Dice Mini App

Base 체인에서 실행되는 1v1 베팅 게임, Farcaster/Base Mini App으로 개발

**[Live Demo](https://triangle-dice-miniapp.vercel.app)**

---

## 게임 소개 (What is Triangle Dice?)

Triangle Dice는 두 명의 플레이어가 USDC를 걸고 경쟁하는 주사위 게임입니다.

### 게임 규칙
1. **매치 생성**: 호스트가 베팅 금액(0.5-10 USDC)을 설정하고 매치 생성
2. **참가**: 게스트가 같은 금액을 걸고 참가
3. **점 배치**: 두 플레이어가 번갈아가며 보드에 점을 배치
4. **선 연결**: 주사위를 굴리고, 나온 숫자만큼 선을 그을 수 있음
5. **삼각형 완성**: 세 개의 점을 모두 연결해 삼각형을 완성하면 +1점
6. **승자 결정**: 더 많은 삼각형을 완성한 플레이어가 승리하고 팟을 가져감

### 왜 만들었나?
- Base Mini App 개발 경험을 쌓고 싶었음
- 스마트 컨트랙트로 안전한 베팅 시스템 구현
- 온체인 게임의 가능성 탐구

---

## 기술 스택 (Tech Stack)

```
Frontend:   Vite + React 19 + TypeScript
Web3:       wagmi 2.x + viem + @coinbase/onchainkit
Mini App:   @farcaster/miniapp-sdk
Contracts:  Foundry (Solidity)
Chain:      Base Sepolia (테스트넷)
Deploy:     Vercel
```

---

## 프로젝트 구조

```
triangle-dice-miniapp/
├── contracts/                 # 스마트 컨트랙트 (Foundry)
│   ├── src/
│   │   ├── MockUSDC.sol          # 테스트용 USDC 토큰
│   │   └── TriangleDiceEscrow.sol # 에스크로 컨트랙트
│   ├── test/
│   └── script/
├── public/
│   ├── .well-known/
│   │   └── farcaster.json        # Mini App manifest
│   └── assets/                   # 앱 아이콘, 이미지
├── src/
│   ├── components/               # React 컴포넌트
│   │   └── WalletConnect.tsx        # 지갑 연결
│   ├── hooks/                    # wagmi 훅
│   │   └── useEscrow.ts             # 컨트랙트 상호작용
│   ├── lib/                      # 유틸리티
│   │   ├── gameEngine.ts            # 게임 로직
│   │   └── dice.ts                  # 주사위 로직
│   ├── pages/                    # 페이지
│   │   ├── Lobby.tsx                # 로비 (매치 생성/참가)
│   │   ├── Board.tsx                # 게임 보드
│   │   └── Result.tsx               # 결과 화면
│   ├── abi/                      # 컨트랙트 ABI
│   ├── main.tsx                  # MiniKitProvider 설정
│   ├── App.tsx                   # 메인 앱
│   └── config.ts                 # wagmi 설정
└── index.html                    # base:app_id 메타태그
```

---

## 컨트랙트 정보 (Contracts)

### 배포된 주소 (Base Sepolia)
- **MockUSDC**: `0x2aC28e4754a9Eeae143399fC1B0B1F9bBe9E2CC3`
- **TriangleDiceEscrow**: `0x0e6Bb9F887B3ca03d942558FaB935701C5A44f21`

### MockUSDC
- ERC20 토큰 (6 decimals)
- 누구나 `mint()` 함수로 테스트 토큰 발행 가능

### TriangleDiceEscrow
- 베팅 범위: 0.5 - 10 USDC
- 타임아웃: 90초 (기본값)
- 수수료: 0.2% (최대 0.02 USDC)
- EIP-712 서명으로 결과 정산

#### 주요 함수
| 함수 | 설명 |
|------|------|
| `createMatch(stakeAmount, timeoutSec)` | 새 매치 생성 |
| `joinMatch(matchId)` | 매치 참가 |
| `startMatch(matchId)` | 게임 시작 (호스트만) |
| `ping(matchId)` | 타임아웃 타이머 리셋 |
| `claimTimeoutWin(matchId)` | 상대방 타임아웃 시 승리 처리 |
| `submitResult(result, sigA, sigB)` | 양측 서명으로 결과 제출 |

---

## Mini App 설정 (Base/Farcaster)

### farcaster.json
Mini App의 메타데이터를 담는 manifest 파일입니다.

```json
{
  "accountAssociation": {
    "header": "...",
    "payload": "...",
    "signature": "..."
  },
  "frame": {
    "name": "Triangle Dice",
    "primaryCategory": "games",
    "tags": ["gaming", "betting", "dice", "pvp", "base"]
  }
}
```

### Account Association 등록 과정
1. **base.dev 접속** (한국에서는 VPN 필요!)
2. **App URL 입력**: `triangle-dice-miniapp.vercel.app`
3. **메타태그 인증**: index.html에 메타태그 추가
4. **지갑 서명**: Verify → Sign
5. **manifest 업데이트**: 받은 값을 farcaster.json에 추가

### 한국에서 주의사항
- Coinbase 서비스가 한국에서 제한됨
- base.dev 접속 시 **미국 VPN** 필요
- Base App 자체는 한국에서 사용 가능 (170개국 지원)

---

## 로컬 개발 (Local Development)

### 필수 조건
- Node.js 18+
- Foundry (`curl -L https://foundry.paradigm.xyz | bash && foundryup`)

### 설치 및 실행

```bash
# 클론
git clone https://github.com/shud26/triangle-dice-miniapp.git
cd triangle-dice-miniapp

# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env
# .env 파일에 컨트랙트 주소 입력

# 개발 서버 실행
npm run dev
```

### 컨트랙트 개발

```bash
cd contracts

# 빌드
forge build

# 테스트
forge test -vv

# 배포 (Base Sepolia)
# contracts/.env 파일 필요:
#   PRIVATE_KEY=...
#   FEE_COLLECTOR=...
#   BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

forge script script/Deploy.s.sol --rpc-url base_sepolia --broadcast
```

---

## 환경 변수

### Frontend (.env)
```bash
VITE_USDC_ADDRESS=0x2aC28e4754a9Eeae143399fC1B0B1F9bBe9E2CC3
VITE_ESCROW_ADDRESS=0x0e6Bb9F887B3ca03d942558FaB935701C5A44f21
VITE_RPC_URL=https://sepolia.base.org
VITE_APP_URL=https://triangle-dice-miniapp.vercel.app
```

### Contracts (contracts/.env)
```bash
PRIVATE_KEY=...
FEE_COLLECTOR=...
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASESCAN_API_KEY=...
```

---

## 현재 상태 (Status)

- ✅ Vercel 배포 완료
- ✅ 스마트 컨트랙트 배포 (Base Sepolia)
- ✅ OnchainKit + MiniKit 통합
- ✅ Account Association 완료
- ✅ 메타데이터 설정 완료
- ⏳ Ready call 디버깅 중
- ⏳ Base App 검색 인덱싱 대기

---

## MVP 한계점

이것은 MVP이므로 다음과 같은 한계가 있습니다:

1. **게임 로직이 오프체인**: 게임 상태가 브라우저에서 관리됨
   - 플레이어 간 신뢰 필요
   - 양측 서명으로 정산

2. **P2P 통신 미구현**: 현재는 수동으로 매치 ID 공유 필요

3. **단일 디바이스**: 페이지 새로고침 시 게임 상태 손실

4. **분쟁 해결 없음**: 결과에 동의하지 않을 경우 온체인 중재 없음

---

## 향후 계획 (Future Plans)

- [ ] Ready call 문제 해결
- [ ] Base App 검색 노출
- [ ] P2P 통신 (WebRTC 또는 릴레이 서버)
- [ ] 온체인 게임 상태 (commit-reveal)
- [ ] 매칭 시스템
- [ ] 리더보드
- [ ] 메인넷 배포 (실제 USDC)

---

## 명령어 정리

```bash
# 개발
npm run dev          # 개발 서버 시작
npm run build        # 프로덕션 빌드
npm run preview      # 빌드 미리보기

# 컨트랙트 (contracts/ 폴더에서)
forge build          # 컨트랙트 빌드
forge test           # 테스트 실행
forge script script/Deploy.s.sol --rpc-url base_sepolia --broadcast
```

---

## 라이선스

MIT

---

*Built with Claude Code*

*마지막 업데이트: 2026-01-24*
