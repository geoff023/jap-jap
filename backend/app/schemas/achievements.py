from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AchievementPublic(BaseModel):
    key: str
    name: str
    description: str
    emoji: str
    earned: bool
    unlocked_at: datetime | None


def achievement_to_public(
    definition: dict[str, Any], unlocked_at: datetime | None
) -> AchievementPublic:
    return AchievementPublic(
        key=definition["key"],
        name=definition["name"],
        description=definition["description"],
        emoji=definition["emoji"],
        earned=unlocked_at is not None,
        unlocked_at=unlocked_at,
    )
