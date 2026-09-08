from typing import Literal

from pydantic import BaseModel

RecommendationReason = Literal["weak_mastery", "try_something_new", "challenge"]


class RecommendationEntry(BaseModel):
    category: str | None
    reason: RecommendationReason
    message: str
    mastery: float | None
    action_label: str
    action_path: str


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationEntry]
