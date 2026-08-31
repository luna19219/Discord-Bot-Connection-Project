import asyncio
import os

from dotenv import load_dotenv
from websockets.asyncio.server import serve

from botlink.parser import BotLinkProgram, parse_file
from botlink.relay import RelayServer


load_dotenv()


async def main():
    host = os.getenv("RELAY_HOST", "127.0.0.1")
    port = int(os.getenv("RELAY_PORT", "8765"))
    env_key = os.getenv("BOTLINK_KEY")

    if not env_key:
        raise RuntimeError(".env에 BOTLINK_KEY를 설정하세요.")

    program = parse_file("examples/Main.botlink")

    if program.key == "$ENV":
        program = BotLinkProgram(key=env_key, rules=program.rules)
    elif program.key != env_key:
        raise RuntimeError(
            "Main.botlink의 key와 .env의 BOTLINK_KEY가 다릅니다."
        )

    relay = RelayServer(program)

    print(f"[BotLink] Relay 시작: ws://{host}:{port}")
    print(f"[BotLink] 규칙 {len(program.rules)}개 로드")

    async with serve(relay.handler, host, port):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
