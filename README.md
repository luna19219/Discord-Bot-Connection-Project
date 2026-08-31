# BotLink

BotLink는 여러 Discord 봇 사이의 이벤트와 행동을 간단한 `.botlink` 문법으로 연결하기 위한 작은 실험용 언어/런타임입니다.
또한 zip파일로 다운해 사용하시는걸 추천드립니다
예:

```botlink
key "$ENV"

when A.message == "!hello" {
    B.send "A봇에서 !hello가 실행됐어!"
}
```

위 규칙은 Bot A가 `!hello` 메시지를 감지했을 때 Bot B가 지정된 채널에 메시지를 보내도록 합니다.

## 구조

```text
BotLink/
├─ botlink/
│  ├─ __init__.py
│  ├─ parser.py
│  └─ relay.py
├─ examples/
│  └─ Main.botlink
├─ bot_a.py
├─ bot_b.py
├─ server.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ LICENSE
```

## 설치

Python 3.11 이상 권장:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

설치:

```bash
pip install -r requirements.txt
```

## 환경 변수

`.env.example`을 복사해서 `.env`를 만든 뒤 값을 채우세요.

```env
BOTLINK_KEY=replace-with-a-long-random-key
BOT_A_TOKEN=your_discord_bot_a_token
BOT_B_TOKEN=your_discord_bot_b_token
BOT_A_NAME=A
BOT_B_NAME=B
BOT_B_DEFAULT_CHANNEL_ID=123456789012345678
RELAY_HOST=127.0.0.1
RELAY_PORT=8765
```

중요: `.env`는 `.gitignore`에 포함되어 있으므로 GitHub에 올리지 마세요.

## Discord 설정

Bot A는 메시지 내용을 읽어야 하므로 Discord Developer Portal에서 **Message Content Intent**를 활성화해야 합니다.

두 봇 모두 테스트 서버에 초대한 뒤 Bot B가 메시지를 보낼 채널 ID를 `BOT_B_DEFAULT_CHANNEL_ID`에 넣으세요.

## 실행

터미널 3개에서 순서대로 실행합니다.

```bash
python server.py
python bot_b.py
python bot_a.py
```

Discord에서 Bot A가 볼 수 있는 채널에:

```text
!hello
```

를 입력하면 Bot B가 기본 채널에 메시지를 전송합니다.

## BotLink v0.1 문법

현재 지원:

```botlink
key "$ENV"

when A.message == "!hello" {
    B.send "안녕!"
}

when A.message == "!ping" {
    B.send "pong"
}
```

지원 기능:
- 이벤트: `message`
- 조건: `==`
- 행동: `send`
- 문자열 값

향후 추가하기 좋은 기능:
- `command`
- `reaction`
- `user_join`
- `voice_join`
- 변수와 조건문
- 여러 대상 봇
- 채널 지정
- WSS/TLS
- 키 회전 및 요청 서명

## 보안

이 코드는 개발/학습용 초기 버전입니다. Relay 서버를 인터넷에 그대로 공개하지 마세요.

실서비스에서는 TLS/WSS, 봇별 인증, 요청 서명, Rate Limit, 재전송 방지 같은 추가 보안이 필요합니다.

Discord Bot Token은 `.botlink`, README, GitHub 저장소에 절대로 넣지 마세요.

## License

MIT
