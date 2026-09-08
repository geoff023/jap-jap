"""Characters and scenarios for Phase 8 (Text Conversation).

Static, not seeded to the database — small enough to version in code, and
this way "which character speaks in which scenario" can never drift out of
sync with a database record. Only 3 scenarios for now, per the master
spec's Phase 8 scope; the remaining characters/scenarios from the full
roster are listed for later phases to pick up without re-designing the cast.
"""

CHARACTERS: dict[str, dict] = {
    "kiko": {
        "key": "kiko",
        "name": "Kiko",
        "emoji": "🦊",
        "specialty": "vocabulary",
        "personality": (
            "Kiko is a precise, patient fox who loves teaching vocabulary. She speaks "
            "clearly, often naming objects and prices explicitly, and gently repeats key "
            "words so they stick."
        ),
    },
    "momo": {
        "key": "momo",
        "name": "Momo",
        "emoji": "🐱",
        "specialty": "casual conversation",
        "personality": (
            "Momo is a warm, casual, enthusiastic cat. She speaks informally and "
            "encouragingly, like chatting with a friend, and keeps the mood light and fun."
        ),
    },
    "kenji": {
        "key": "kenji",
        "name": "Kenji",
        "emoji": "🐸",
        "specialty": "grammar",
        "personality": (
            "Kenji is a methodical, encouraging frog who explains things step by step. He "
            "speaks in clear, well-formed sentences and doesn't mind repeating himself in "
            "a slightly different way if it helps."
        ),
    },
    "yuki": {
        "key": "yuki",
        "name": "Yuki",
        "emoji": "🐰",
        "specialty": "JLPT",
        "personality": (
            "Yuki is a focused, exam-oriented rabbit. She is motivating and a little "
            "brisk, and likes to note which JLPT level a phrase would appear at."
        ),
    },
    "ponta": {
        "key": "ponta",
        "name": "Ponta",
        "emoji": "🐼",
        "specialty": "culture",
        "personality": (
            "Ponta is a curious, relaxed panda who loves sharing cultural trivia. He "
            "brings up small cultural notes naturally in conversation without lecturing."
        ),
    },
}

SCENARIOS: dict[str, dict] = {
    "ramen_shop": {
        "key": "ramen_shop",
        "title": "Ramen Shop",
        "emoji": "🍜",
        "description": "You've just sat down at the counter of a small ramen shop.",
        "character_key": "momo",
        "opening_line": "いらっしゃいませ！何にしますか？",
        "opening_translation": "Welcome! What would you like to order?",
    },
    "convenience_store": {
        "key": "convenience_store",
        "title": "Convenience Store",
        "emoji": "🏪",
        "description": "You're checking out at a convenience store register.",
        "character_key": "kiko",
        "opening_line": "いらっしゃいませ。袋はご利用ですか？",
        "opening_translation": "Welcome. Would you like a bag?",
    },
    "train_station": {
        "key": "train_station",
        "title": "Train Station",
        "emoji": "🚉",
        "description": "You're at a train station information counter, asking for directions.",
        "character_key": "kenji",
        "opening_line": "こんにちは。今日はどちらまで行かれますか？",
        "opening_translation": "Hello. Where are you headed today?",
    },
}


def get_scenario(key: str) -> dict:
    return SCENARIOS[key]


def get_character(key: str) -> dict:
    return CHARACTERS[key]


def list_scenarios() -> list[dict]:
    return [
        {**scenario, "character": get_character(scenario["character_key"])}
        for scenario in SCENARIOS.values()
    ]
