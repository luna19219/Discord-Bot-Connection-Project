from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class BotLinkRule:
    source_bot: str
    event: str
    expected_value: str
    target_bot: str
    action: str
    action_value: str


@dataclass(frozen=True)
class BotLinkProgram:
    key: str
    rules: list[BotLinkRule]


KEY_RE = re.compile(
    r'^\s*key\s+"(?P<key>(?:[^"\\]|\\.)*)"\s*$',
    re.MULTILINE,
)

RULE_RE = re.compile(
    r"""
    when\s+
    (?P<source>[A-Za-z_][A-Za-z0-9_]*)\.
    (?P<event>[A-Za-z_][A-Za-z0-9_]*)
    \s*==\s*
    "(?P<expected>(?:[^"\\]|\\.)*)"
    \s*\{
        \s*
        (?P<target>[A-Za-z_][A-Za-z0-9_]*)\.
        (?P<action>[A-Za-z_][A-Za-z0-9_]*)
        \s+
        "(?P<value>(?:[^"\\]|\\.)*)"
        \s*;?
        \s*
    \}
    """,
    re.VERBOSE | re.MULTILINE | re.DOTALL,
)


def _decode(value: str) -> str:
    return value.replace(r'\"', '"').replace(r'\\', '\\')


def parse_text(text: str) -> BotLinkProgram:
    key_match = KEY_RE.search(text)
    if not key_match:
        raise ValueError('BotLink 파일에 key "..." 선언이 필요합니다.')

    key = _decode(key_match.group("key"))
    rules: list[BotLinkRule] = []

    for match in RULE_RE.finditer(text):
        rules.append(
            BotLinkRule(
                source_bot=match.group("source"),
                event=match.group("event"),
                expected_value=_decode(match.group("expected")),
                target_bot=match.group("target"),
                action=match.group("action"),
                action_value=_decode(match.group("value")),
            )
        )

    if not rules:
        raise ValueError("실행 가능한 when 규칙을 찾지 못했습니다.")

    return BotLinkProgram(key=key, rules=rules)


def parse_file(path: str | Path) -> BotLinkProgram:
    return parse_text(Path(path).read_text(encoding="utf-8"))
