# Day 53~55 - 2026-05월 중순 — hunslog_bot 블로그 자동화

## hunslog_bot 개발

### 개요
봇 운영 데이터 → Ollama(qwen2.5:14b)로 글 생성 → 텔레그램 발송 → 1시간 후 티스토리 자동 발행

### 플로우
```
nado_grid 로그 수집
    ↓
qwen2.5:14b 글 생성 (500~800자)
    ↓
텔레그램으로 초안 발송 (/draft)
    ↓
승인 후 1시간 타이머
    ↓
티스토리 자동 발행 (/publish)
```

### 텔레그램 명령어
- `/draft` - 새 글 초안 생성
- `/publish` - 즉시 발행
- `/regen` - 다시 생성
- `/skip` - 오늘 건너뜀
- `/full` - 전체 자동화 (draft → 1h → publish)
- `/status` - 현재 상태 확인

### 스케줄
매일 오전 10시~오후 10시 사이 랜덤 시각 (LaunchAgent)

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key><integer>10</integer>
    <key>Minute</key><integer>0</integer>
</dict>
```

### 글 주제 풀
- "오늘 스톱로스가 몇 번 발동했나"
- "핑퐁봇 라운드트립 기록"
- "TimesFM이 맞춘 날 vs 틀린 날"
- 봇 운영하면서 배운 것들

### 블로그
- **hunslog.tistory.com** — 봇 운영 경험 "훈수" 버전 (솔직 후기)
- 2026-04-17: 첫 글 발행 ("나도봇 스톱로스가 발동했다 — 손절은 기능이다")
- AdSense 재심사 신청 완료, 결과 대기 중

## 배운 것

- Ollama로 반복 글쓰기 자동화는 생각보다 퀄리티가 괜찮다
- 텔레그램 인터랙션 → 사람이 승인하는 단계가 퀄리티 관리에 필수
- 블로그 = 봇 로그를 글로 변환하는 과정 (데이터가 곧 콘텐츠)
