"""Curated target phrases for Phase 9 (Speech-to-Text) pronunciation
practice.

Static, not seeded to the database — same rationale as Phase 8's
conversation_data.py: a small, curated set versioned in code guarantees a
phrase and its "correct" target text can never drift out of sync, and
needs no database migration to add later phases' content.
"""

SPEAKING_PROMPTS: dict[str, dict] = {
    "n5-greeting": {
        "key": "n5-greeting",
        "level": "N5",
        "target_text": "おはようございます",
        "target_reading": "おはようございます",
        "target_translation": "Good morning.",
    },
    "n5-introduction": {
        "key": "n5-introduction",
        "level": "N5",
        "target_text": "はじめまして",
        "target_reading": "はじめまして",
        "target_translation": "Nice to meet you.",
    },
    "n5-thanks": {
        "key": "n5-thanks",
        "level": "N5",
        "target_text": "ありがとうございます",
        "target_reading": "ありがとうございます",
        "target_translation": "Thank you.",
    },
    "n5-where-station": {
        "key": "n5-where-station",
        "level": "N5",
        "target_text": "駅はどこですか",
        "target_reading": "えきはどこですか",
        "target_translation": "Where is the station?",
    },
    "n4-daily-routine": {
        "key": "n4-daily-routine",
        "level": "N4",
        "target_text": "毎朝六時に起きます",
        "target_reading": "まいあさろくじにおきます",
        "target_translation": "I wake up at six every morning.",
    },
    "n4-weather": {
        "key": "n4-weather",
        "level": "N4",
        "target_text": "今日は雨が降りそうです",
        "target_reading": "きょうはあめがふりそうです",
        "target_translation": "It looks like it's going to rain today.",
    },
    "n3-opinion": {
        "key": "n3-opinion",
        "level": "N3",
        "target_text": "この映画は面白いと思います",
        "target_reading": "このえいがはおもしろいとおもいます",
        "target_translation": "I think this movie is interesting.",
    },
    "n2-request": {
        "key": "n2-request",
        "level": "N2",
        "target_text": "もう少し詳しく説明していただけますか",
        "target_reading": "もうすこしくわしくせつめいしていただけますか",
        "target_translation": "Could you explain in a bit more detail?",
    },
    "n1-apology": {
        "key": "n1-apology",
        "level": "N1",
        "target_text": "誠に申し訳ございませんでした",
        "target_reading": "まことにもうしわけございませんでした",
        "target_translation": "I am truly sorry.",
    },
}


def get_prompt(key: str) -> dict:
    return SPEAKING_PROMPTS[key]


def list_prompts(level: str | None = None) -> list[dict]:
    prompts = list(SPEAKING_PROMPTS.values())
    if level is not None:
        prompts = [p for p in prompts if p["level"] == level]
    return prompts
