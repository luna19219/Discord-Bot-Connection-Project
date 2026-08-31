from __future__ import annotations

import asyncio
import json
from typing import Any

import websockets


class RelayServer:
    def __init__(self, program):
        self.program = program
        self.clients = {}
        self.lock = asyncio.Lock()

    async def send_json(self, websocket, payload: dict[str, Any]):
        await websocket.send(json.dumps(payload, ensure_ascii=False))

    async def register(self, websocket, payload):
        if payload.get("type") != "register":
            await self.send_json(websocket, {
                "type": "error",
                "message": "첫 메시지는 register여야 합니다."
            })
            return None

        if payload.get("key") != self.program.key:
            await self.send_json(websocket, {
                "type": "error",
                "message": "BotLink 키가 올바르지 않습니다."
            })
            return None

        bot_name = str(payload.get("bot", "")).strip()
        if not bot_name:
            await self.send_json(websocket, {
                "type": "error",
                "message": "bot 이름이 필요합니다."
            })
            return None

        async with self.lock:
            self.clients[bot_name] = websocket

        await self.send_json(websocket, {
            "type": "registered",
            "bot": bot_name
        })
        print(f"[Relay] {bot_name} 연결됨")
        return bot_name

    async def handle_event(self, websocket, registered_bot, payload):
        if payload.get("key") != self.program.key:
            await self.send_json(websocket, {
                "type": "error",
                "message": "잘못된 BotLink 키입니다."
            })
            return

        if payload.get("type") != "event":
            return

        source = str(payload.get("bot", ""))
        event = str(payload.get("event", ""))
        value = str(payload.get("value", ""))

        if source != registered_bot:
            await self.send_json(websocket, {
                "type": "error",
                "message": "등록된 봇 이름과 event.bot이 다릅니다."
            })
            return

        for rule in self.program.rules:
            if (
                rule.source_bot == source
                and rule.event == event
                and rule.expected_value == value
            ):
                target = self.clients.get(rule.target_bot)
                if target is None:
                    print(f"[Relay] 대상 {rule.target_bot} 미연결")
                    continue

                await self.send_json(target, {
                    "type": "action",
                    "key": self.program.key,
                    "from": source,
                    "target": rule.target_bot,
                    "action": rule.action,
                    "value": rule.action_value,
                })
                print(
                    f"[Relay] {source}.{event} -> "
                    f"{rule.target_bot}.{rule.action}"
                )

    async def handler(self, websocket):
        bot_name = None
        try:
            payload = json.loads(await websocket.recv())
            bot_name = await self.register(websocket, payload)
            if not bot_name:
                await websocket.close()
                return

            async for raw in websocket:
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    await self.send_json(websocket, {
                        "type": "error",
                        "message": "JSON 형식이 아닙니다."
                    })
                    continue

                await self.handle_event(websocket, bot_name, payload)

        except websockets.ConnectionClosed:
            pass
        finally:
            if bot_name:
                async with self.lock:
                    if self.clients.get(bot_name) is websocket:
                        self.clients.pop(bot_name, None)
                print(f"[Relay] {bot_name} 연결 해제")
