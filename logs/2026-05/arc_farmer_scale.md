# Day 49~52 - 2026-05월 초 — arc_farmer 780계정 확대

## arc_farmer 대규모 스케일업

### 배경
ink_farmer 30계정으로 운영하던 것을 Arc testnet 전용으로 분리하고, 계정을 30 → 780개로 대폭 확대.

### 구조 변경
- **ink_farmer** (기존): 30계정, Ink Chain 온체인 활동 (swap, GM, Nado 트랜잭션)
- **arc_farmer** (신규): 780계정, Arc testnet 파밍 (deploy, NFT mint, GM, swap, FlowFi)

### arc_farmer 핵심 설계

```python
ACTION_POOL = [
    ("deploy",    "컨트랙트배포",  deploy_contract),
    ("nft",       "NFT민트",       mint_nft),
    ("swap",      "DEX스왑",       swap_usdc_to_eurc),
    ("flowfi",    "FlowFi예치",    deposit_and_withdraw),
    ("gm",        "GM스트릭",      send_gm),
    ("flowonarc", "FlowOnArc",     flowonarc_all),
]
SKIP_PROBABILITY = 0.12  # 12% 확률로 오늘 스킵 (인간처럼)
ACCOUNTS_PER_RUN_RATIO = 0.08  # 전체의 8%씩 하루에 실행
```

### LaunchAgent (StartCalendarInterval)
- 매일 09:30 자동 실행 후 종료 (KeepAlive X)
- 처음엔 하루 12~15개 계정 처리 → 최적화 후 25~60개

### 삽질 포인트
- `PID=0`이라도 정상! StartCalendarInterval은 실행 완료 후 PID가 0이 됨
- Faucet 30분 쿨다운이 진짜 병목이었음 → Faucet 실패 시 즉시 스킵으로 해결

### 처리 속도 개선 (2026-05-28)
```python
# Before
DELAY_BETWEEN_ACCOUNTS = (300, 900)  # 5~15분
ACCOUNTS_PER_RUN_RATIO = 0.05        # 5%

# After
DELAY_BETWEEN_ACCOUNTS = (120, 360)  # 2~6분
ACCOUNTS_PER_RUN_RATIO = 0.08        # 8%
```

Faucet 실패 계정은 30분 기다리지 않고 바로 다음 계정으로 스킵:
```python
faucet_result = run_faucet_for_account(account, state, dry_run, faucet_counter)
if faucet_result == "failed":
    print(f"  → Faucet 실패, 가스비 없음 — 계정 스킵")
    return [{"action": "faucet_skip", "status": "skipped"}]
```

## 배운 것

- 다계정 자동화의 핵심은 "실패 처리"임. 성공 케이스보다 실패 케이스가 훨씬 많다.
- 780개 계정 × 한 바퀴 = 39일. 계정 추가보다 처리 속도가 더 중요함.
- `StartCalendarInterval` vs `KeepAlive` 차이: 반복 작업은 전자가 맞음.
