from datetime import datetime, timezone
from typing import Any

from app.ai.base import AIService
from app.core.conversation_data import get_character, get_scenario, list_scenarios
from app.repositories.conversation_repository import (
    ConversationMessageRepository,
    ConversationSessionRepository,
)
from app.repositories.profile_repository import LearnerProfileRepository

# Bounds how much conversation history is replayed into each Gemini prompt —
# enough to keep the character/scene consistent without letting the prompt
# (and cost) grow unbounded across a very long conversation.
HISTORY_LIMIT = 20
XP_PER_MESSAGE = 3


class ProfileRequiredError(Exception):
    """Raised when a learner tries to earn XP before completing onboarding."""


class SessionNotFoundError(Exception):
    pass


class ConversationService:
    def __init__(
        self,
        ai: AIService,
        sessions: ConversationSessionRepository,
        messages: ConversationMessageRepository,
        profiles: LearnerProfileRepository,
    ):
        self._ai = ai
        self._sessions = sessions
        self._messages = messages
        self._profiles = profiles

    def list_scenarios(self) -> list[dict[str, Any]]:
        return list_scenarios()

    async def start_session(self, user_id: str, scenario_key: str, level: str) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        scenario = get_scenario(scenario_key)
        now = datetime.now(timezone.utc)

        session = await self._sessions.create(
            {
                "user_id": user_id,
                "scenario_key": scenario_key,
                "character_key": scenario["character_key"],
                "level": level,
                "started_at": now,
                "last_message_at": now,
                "message_count": 1,
            }
        )
        opening = await self._messages.create(
            {
                "session_id": str(session["_id"]),
                "role": "character",
                "content": scenario["opening_line"],
                "translation": scenario["opening_translation"],
                "created_at": now,
            }
        )
        return {"session": session, "messages": [opening]}

    async def get_session(self, user_id: str, session_id: str) -> dict[str, Any]:
        session = await self._sessions.find_by_id(session_id)
        if session is None or session["user_id"] != user_id:
            raise SessionNotFoundError(session_id)
        messages = await self._messages.list_by_session(session_id)
        return {"session": session, "messages": messages}

    async def list_sessions(self, user_id: str) -> list[dict[str, Any]]:
        return await self._sessions.list_by_user(user_id)

    async def send_message(self, user_id: str, session_id: str, content: str) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        session = await self._sessions.find_by_id(session_id)
        if session is None or session["user_id"] != user_id:
            raise SessionNotFoundError(session_id)

        scenario = get_scenario(session["scenario_key"])
        character = get_character(session["character_key"])

        history_docs = await self._messages.list_by_session(session_id, limit=HISTORY_LIMIT)
        history = [{"role": doc["role"], "content": doc["content"]} for doc in history_docs]

        # Only persist the user's turn once we know the character replied —
        # if continue_conversation raises, storing it anyway would leave a
        # dangling user turn with no reply, which would then get replayed as
        # history into the *next* prompt and confuse the character.
        reply = await self._ai.continue_conversation(
            character["name"],
            character["personality"],
            scenario["title"],
            scenario["description"],
            session["level"],
            history,
            content,
        )

        now = datetime.now(timezone.utc)
        user_message = await self._messages.create(
            {
                "session_id": session_id,
                "role": "user",
                "content": content,
                "translation": None,
                "created_at": now,
            }
        )

        reply_time = datetime.now(timezone.utc)
        character_message = await self._messages.create(
            {
                "session_id": session_id,
                "role": "character",
                "content": reply.reply,
                "translation": reply.translation,
                "created_at": reply_time,
            }
        )
        await self._sessions.touch(session_id, reply_time, increment=2)

        updated_profile = await self._profiles.increment_xp(user_id, XP_PER_MESSAGE)
        assert updated_profile is not None

        return {
            "user_message": user_message,
            "character_message": character_message,
            "xp_earned": XP_PER_MESSAGE,
            "total_xp": updated_profile["xp"],
        }
