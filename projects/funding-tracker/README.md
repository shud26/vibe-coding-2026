# 멀티 DEX 펀딩비 트래커

여러 퍼프 DEX의 펀딩비를 모니터링하고 차익거래 기회를 알려줍니다.

---

## 지원 DEX

| DEX | 체인 | 상태 |
|-----|------|------|
| Hyperliquid | 자체 L1 | ✅ |
| Pacifica | Solana | ✅ |
| Variational | Arbitrum | ✅ |

---

## 기능

### 1. 실시간 펀딩비 모니터링
```
=======================================================
코인      Hyperliquid     Pacifica  Variational
-------------------------------------------------------
BTC        +0.0013%     +0.0010%     +0.0077%
ETH        +0.0013%     +0.0015%     +0.0101%
SOL        +0.0013%     -0.0004%     -0.0076%
=======================================================
```

### 2. 차익거래 기회 알림
같은 코인의 펀딩비가 DEX별로 다를 때 알림
- A 거래소 +0.05%, B 거래소 -0.02% → 차익 0.07%
- A에서 숏 + B에서 롱 = 펀딩비 수익

### 3. 고펀딩 알림
단일 DEX 펀딩비가 ±0.01% 이상일 때 알림

---

## 사용법

```bash
# 한 번만 체크
python3 multi_dex_funding.py --once

# 백그라운드 모니터링 (5분마다)
nohup python3 multi_dex_funding.py > multi_funding.log 2>&1 &

# 로그 확인
tail -f multi_funding.log

# 종료
pkill -f multi_dex_funding.py
```

---

## 설정 변경

`multi_dex_funding.py` 파일 상단:

```python
COINS = ["BTC", "ETH", "SOL"]           # 추적할 코인
SINGLE_THRESHOLD = 0.01                  # 단일 알림 기준 (%)
ARBITRAGE_THRESHOLD = 0.02               # 차익 알림 기준 (%)
```

---

## 파일 구조

```
funding-tracker/
├── funding_tracker.py      # 단일 DEX (Hyperliquid)
├── multi_dex_funding.py    # 멀티 DEX (추천)
└── README.md
```

---

## 펀딩비란?

| 펀딩비 | 의미 | 전략 |
|--------|------|------|
| 🔴 양수 | 롱이 숏에게 지불 | 숏이 유리 |
| 🟢 음수 | 숏이 롱에게 지불 | 롱이 유리 |

---

*Built with Claude Code*
