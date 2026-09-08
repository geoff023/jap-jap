"""Achievement catalog for Phase 11 (Achievements).

Seeded into the `achievements` collection at startup — same
seed-from-code-into-Mongo pattern as Phase 3's VOCABULARY_N5/GRAMMAR_N5,
unlike Phase 8/9's characters/scenarios/speaking prompts (which stay
purely in-code since they're referenced by key when building AI prompts,
not listed as a catalog the way achievements are).
"""

ACHIEVEMENTS: list[dict] = [
    {
        "key": "first_steps",
        "name": "First Steps",
        "description": "Complete your first quiz, flashcard set, or test.",
        "emoji": "🎯",
    },
    {
        "key": "century_club",
        "name": "Century Club",
        "description": "Earn 100 XP.",
        "emoji": "💯",
    },
    {
        "key": "high_scorer",
        "name": "High Scorer",
        "description": "Earn 500 XP.",
        "emoji": "🏆",
    },
    {
        "key": "xp_master",
        "name": "XP Master",
        "description": "Earn 1000 XP.",
        "emoji": "👑",
    },
    {
        "key": "chatterbox",
        "name": "Chatterbox",
        "description": "Start your first conversation with an AI character.",
        "emoji": "💬",
    },
    {
        "key": "speaker",
        "name": "Speaker",
        "description": "Complete your first Speaking Practice attempt.",
        "emoji": "🎤",
    },
    {
        "key": "bookworm",
        "name": "Bookworm",
        "description": "Answer a mini story's reading comprehension question.",
        "emoji": "📖",
    },
    {
        "key": "well_rounded",
        "name": "Well-Rounded",
        "description": (
            "Try every practice type: vocabulary, grammar, reading, speaking, and conversation."
        ),
        "emoji": "🌟",
    },
    {
        "key": "perfectionist",
        "name": "Perfectionist",
        "description": "Reach 90% mastery in a category (with at least 5 attempts).",
        "emoji": "💎",
    },
    {
        "key": "test_taker",
        "name": "Test Taker",
        "description": "Complete 5 tests.",
        "emoji": "📝",
    },
]
