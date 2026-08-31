import asyncio
import json
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import websockets


load_dotenv()

TOKEN = os.getenv("BOT_B_TOKEN")
BOT_NAME = os.getenv("BOT_B_NAME", "B")
BOTLINK_KEY = os.getenv("BOTLINK_KEY")
CHANNEL_ID = int(os.getenv("BOT_B_DEFAULT_CHANNEL_ID", "0"))
HOST = os.getenv("RELAY_HOST", "127.0.0.1")
PORT = os.getenv("RELAY_PORT", "8765")
RELAY_URL = f"ws://{HOST}:{PORT}"

if not TOKEN:
    raise RuntimeError(".env에 BOT_B_TOKEN을 설정하세요.")
if not BOTLINK_KEY:
    raise RuntimeError(".env에 BOTLINK_KEY를 설정하세요.")
if not CHANNEL_ID:
    raise RuntimeError(".env에 BOT_B_DEFAULT_CHANNEL_ID를 설정하세요.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def execute_action(payload):
    if payload.get("key") != BOTLINK_KEY:
        return
    if payload.get("target") != BOT_NAME:
        return

    action = payload.get("action")
    value = str(payload.get("value", ""))

    if action == "send":
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(CHANNEL_ID)

        await channel.send(value)
        print(f"[{BOT_NAME}] 메시지 전송: {value}")
    else:
        print(f"[{BOT_NAME}] 지원하지 않는 action: {action}")


async def connect_relay():
    while not bot.is_closed():
        try:
            async with websockets.connect(RELAY_URL) as websocket:
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
                    payload = json.loads(raw)
                    if payload.get("type") == "action":
                        await execute_action(payload)

        except Exception as exc:
            print(f"[{BOT_NAME}] Relay 오류: {exc}")
            await asyncio.sleep(3)


@bot.event
async def on_ready():
    print(f"[{BOT_NAME}] Discord 로그인: {bot.user}")


async def runner():
    relay_task = asyncio.create_task(connect_relay())
    try:
        await bot.start(TOKEN)
    finally:
        relay_task.cancel()


if __name__ == "__main__":
    asyncio.run(runner())
