import asyncio
import json
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import websockets


load_dotenv()

TOKEN = os.getenv("BOT_A_TOKEN")
BOT_NAME = os.getenv("BOT_A_NAME", "A")
BOTLINK_KEY = os.getenv("BOTLINK_KEY")
HOST = os.getenv("RELAY_HOST", "127.0.0.1")
PORT = os.getenv("RELAY_PORT", "8765")
RELAY_URL = f"ws://{HOST}:{PORT}"

if not TOKEN:
    raise RuntimeError(".env에 BOT_A_TOKEN을 설정하세요.")
if not BOTLINK_KEY:
    raise RuntimeError(".env에 BOTLINK_KEY를 설정하세요.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

relay_socket = None


async def connect_relay():
    global relay_socket

    while not bot.is_closed():
        try:
            async with websockets.connect(RELAY_URL) as websocket:
                relay_socket = websocket

                await websocket.send(json.dumps({
                    "type": "register",
                    "key": BOTLINK_KEY,
                    "bot": BOT_NAME,
                }, ensure_ascii=False))

                response = json.loads(await websocket.recv())
                if response.get("type") != "registered":
                    raise RuntimeError(response.get("message", "등록 실패"))

                print(f"[{BOT_NAME}] Relay 연결 완료")

                async for raw in websocket:
                    print(f"[{BOT_NAME}] Relay: {raw}")

        except Exception as exc:
            relay_socket = None
            print(f"[{BOT_NAME}] Relay 오류: {exc}")
            await asyncio.sleep(3)


@bot.event
async def on_ready():
    print(f"[{BOT_NAME}] Discord 로그인: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if relay_socket is not None:
        try:
            await relay_socket.send(json.dumps({
                "type": "event",
                "key": BOTLINK_KEY,
                "bot": BOT_NAME,
                "event": "message",
                "value": message.content,
            }, ensure_ascii=False))
        except Exception as exc:
            print(f"[{BOT_NAME}] 이벤트 전송 실패: {exc}")

    await bot.process_commands(message)


async def runner():
    relay_task = asyncio.create_task(connect_relay())
    try:
        await bot.start(TOKEN)
    finally:
        relay_task.cancel()


if __name__ == "__main__":
    asyncio.run(runner())
