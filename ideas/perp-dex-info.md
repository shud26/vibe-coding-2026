# Perp DEX 정보 모음

> 2026-01-18 조사 내용

---

## 1. Hyperliquid

| 항목 | 내용 |
|------|------|
| 체인 | 자체 L1 (HyperBFT) |
| 특징 | 0.2초 체결, 200k TPS, 온체인 오더북 |
| 레버리지 | 최대 50x |
| API | ✅ REST API |
| 문서 | https://hyperliquid.gitbook.io/hyperliquid-docs |

**펀딩비 API:**
```python
POST https://api.hyperliquid.xyz/info
{"type": "metaAndAssetCtxs"}
# 응답에서 funding 필드 사용
```

---

## 2. Pacifica

| 항목 | 내용 |
|------|------|
| 체인 | Solana |
| 특징 | 前 FTX COO 설립, 10ms 미만 체결 |
| 레버리지 | 5x ~ 50x |
| 마켓 | 35+ 자산 |
| API | ✅ REST + WebSocket |
| 문서 | https://docs.pacifica.fi |

**펀딩비 특징:**
- 5초마다 펀딩비 계산
- 1시간마다 정산
- Oracle 가격 3초마다 갱신

**API 엔드포인트:**
- REST: `/api-documentation/api`
- 펀딩비 조회: Markets API → "Get historical funding"
- WebSocket: 실시간 구독 가능

---

## 3. Variational

| 항목 | 내용 |
|------|------|
| 체인 | Arbitrum (Ethereum L2) |
| 특징 | 제로 수수료, 손실 환불 (5% 확률) |
| 레버리지 | 다양함 |
| TVL | $33M (2025.10 기준) |
| 누적 거래량 | $2.5B |
| API | ✅ REST API |
| 문서 | https://docs.variational.io |

**투자:**
- Bain Capital Crypto
- Coinbase Ventures
- Peak XV (Sequoia India)
- Dragonfly

**API 엔드포인트:**
- API 문서: `/technical-documentation/api`
- 펀딩비: `/omni/trading/funding-rates`

---

## 4. Nado

| 항목 | 내용 |
|------|------|
| 체인 | Ink L2 (Kraken의 L2) |
| 특징 | 통합 마진 (스팟+마진+퍼프), 5-15ms 체결 |
| 팀 | 前 Kraken 엔지니어들 |
| OI | ~$90M |
| 일일 거래량 | ~$500M |
| 문서 | https://www.nado.xyz |

**특징:**
- CLOB (Central Limit Order Book) DEX
- 셀프 커스터디
- 스팟, 마진, 퍼프 통합 마진

---

## 5. Extended

| 항목 | 내용 |
|------|------|
| 체인 | Starknet |
| 특징 | 100x 레버리지, STARK proofs |
| 마켓 | 50+ 자산 |
| 지원 지갑 | MetaMask, WalletConnect, Starknet |
| 문서 | https://extended.exchange |

**특징:**
- 원래 StarkEx에서 Starknet으로 이전
- 크로스체인 접근성
- BTC 기반 Vault 전략 지원
- ⚠️ 미국 사용자 불가

---

## 기타 주요 Perp DEX

| DEX | 체인 | 특징 |
|-----|------|------|
| GMX | Arbitrum, Avalanche | 가장 유명한 perp DEX |
| dYdX | Cosmos (자체체인) | 기관급 거래소 |
| Jupiter Perps | Solana | Solana 66% 점유율 |
| Vertex | Arbitrum | 하이브리드 오더북 |
| Aevo | Ethereum L2 | 옵션 + 퍼프 |

---

## 펀딩비 차익거래 전략

```
1. 여러 DEX 펀딩비 모니터링
2. 같은 자산, 다른 펀딩비 발견
3. 높은 곳에서 숏 + 낮은 곳에서 롱
4. 펀딩비 차이만큼 수익

예시:
- Hyperliquid BTC: +0.05%
- Pacifica BTC: -0.02%
- 차이: 0.07%
→ HL 숏 + Pacifica 롱 = 0.07% 차익
```

---

*마지막 업데이트: 2026-01-18*
