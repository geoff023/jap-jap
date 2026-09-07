from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.base import AIService, AIServiceError
from app.api.deps import get_ai_interaction_repository, get_ai_service, get_current_user
from app.repositories.ai_interaction_repository import AIInteractionRepository
from app.schemas.ai import (
    GrammarExplanation,
    GrammarExplanationRequest,
    MistakeExplanation,
    MistakeExplanationRequest,
    VocabularyExplanation,
    VocabularyExplanationRequest,
)

router = APIRouter()


def _ai_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="The AI tutor couldn't produce an explanation. Please try again.",
    )


@router.post("/explain/grammar", response_model=GrammarExplanation)
async def explain_grammar(
    payload: GrammarExplanationRequest,
    current_user: dict = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
    interactions: AIInteractionRepository = Depends(get_ai_interaction_repository),
) -> GrammarExplanation:
    try:
        explanation = await ai.explain_grammar(payload.concept, payload.context)
    except AIServiceError as exc:
        raise _ai_unavailable() from exc
    await interactions.record(str(current_user["_id"]), "grammar_explanation", payload.concept)
    return explanation


@router.post("/explain/vocabulary", response_model=VocabularyExplanation)
async def explain_vocabulary(
    payload: VocabularyExplanationRequest,
    current_user: dict = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
    interactions: AIInteractionRepository = Depends(get_ai_interaction_repository),
) -> VocabularyExplanation:
    try:
        explanation = await ai.explain_vocabulary(payload.term, payload.context)
    except AIServiceError as exc:
        raise _ai_unavailable() from exc
    await interactions.record(str(current_user["_id"]), "vocabulary_explanation", payload.term)
    return explanation


@router.post("/explain/mistake", response_model=MistakeExplanation)
async def explain_mistake(
    payload: MistakeExplanationRequest,
    current_user: dict = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
    interactions: AIInteractionRepository = Depends(get_ai_interaction_repository),
) -> MistakeExplanation:
    try:
        explanation = await ai.explain_mistake(
            payload.category, payload.concept, payload.user_answer, payload.correct_answer
        )
    except AIServiceError as exc:
        raise _ai_unavailable() from exc
    await interactions.record(str(current_user["_id"]), "mistake_explanation", payload.concept)
    return explanation
