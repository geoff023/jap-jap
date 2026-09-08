from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.conversation_data import get_character
from app.schemas.profile import JLPTLevel


class ScenarioKey(str, Enum):
    RAMEN_SHOP = "ramen_shop"
    CONVENIENCE_STORE = "convenience_store"
    TRAIN_STATION = "train_station"


class ConversationReply(BaseModel):
    """Gemini's structured output for one in-character conversation turn."""

    reply: str = Field(min_length=1, max_length=500)
    translation: str = Field(min_length=1, max_length=500)


class CharacterPublic(BaseModel):
    key: str
    name: str
    emoji: str
    specialty: str


class ScenarioPublic(BaseModel):
    key: str
    title: str
    emoji: str
    description: str
    character: CharacterPublic


class StartConversationRequest(BaseModel):
    scenario: ScenarioKey
    level: JLPTLevel


class MessagePublic(BaseModel):
    role: str
    content: str
    translation: str | None = None
    created_at: datetime


class ConversationSessionSummary(BaseModel):
    id: str
    scenario: ScenarioKey
    character_name: str
    character_emoji: str
    level: JLPTLevel
    started_at: datetime
    last_message_at: datetime
    message_count: int


class ConversationSessionDetail(BaseModel):
    id: str
    scenario: ScenarioKey
    character: CharacterPublic
    level: JLPTLevel
    started_at: datetime
    messages: list[MessagePublic]


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class SendMessageResponse(BaseModel):
    user_message: MessagePublic
    character_message: MessagePublic
    xp_earned: int
    total_xp: int


def message_to_public(doc: dict[str, Any]) -> MessagePublic:
    return MessagePublic(
        role=doc["role"],
        content=doc["content"],
        translation=doc.get("translation"),
        created_at=doc["created_at"],
    )


def session_to_summary(doc: dict[str, Any]) -> ConversationSessionSummary:
    character = get_character(doc["character_key"])
    return ConversationSessionSummary(
        id=str(doc["_id"]),
        scenario=doc["scenario_key"],
        character_name=character["name"],
        character_emoji=character["emoji"],
        level=doc["level"],
        started_at=doc["started_at"],
        last_message_at=doc["last_message_at"],
        message_count=doc.get("message_count", 0),
    )


def session_to_detail(
    session_doc: dict[str, Any], message_docs: list[dict[str, Any]]
) -> ConversationSessionDetail:
    character = get_character(session_doc["character_key"])
    return ConversationSessionDetail(
        id=str(session_doc["_id"]),
        scenario=session_doc["scenario_key"],
        character=CharacterPublic(**character),
        level=session_doc["level"],
        started_at=session_doc["started_at"],
        messages=[message_to_public(m) for m in message_docs],
    )
