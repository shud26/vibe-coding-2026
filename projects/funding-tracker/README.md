# 펀딩비 트래커

Hyperliquid 거래소의 펀딩비를 모니터링하고 텔레그램으로 알림을 보내줍니다.

## 펀딩비란?

- **양수 펀딩비**: 롱 포지션이 숏 포지션에게 지불 → 숏이 유리
- **음수 펀딩비**: 숏 포지션이 롱 포지션에게 지불 → 롱이 유리

## 사용법

```bash
# 한 번만 체크
python3 funding_tracker.py --once

# 백그라운드 모니터링 (5분마다 체크)
nohup python3 funding_tracker.py > funding.log 2>&1 &

# 로그 확인
tail -f funding.log

# 프로세스 종료
pkill -f funding_tracker.py
```

## 추적 코인

BTC, ETH, SOL, DOGE, XRP, AVAX, LINK, ARB, OP, SUI

## 알림 기준

펀딩비가 **±0.01%** 이상일 때 텔레그램 알림
