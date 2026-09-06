from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_vocabulary_repository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.profile import JLPTLevel
from app.schemas.vocabulary import VocabularyItem, vocabulary_to_public

router = APIRouter()


@router.get("", response_model=list[VocabularyItem])
async def list_vocabulary(
    level: JLPTLevel | None = None,
    current_user: dict = Depends(get_current_user),
    vocabulary: VocabularyRepository = Depends(get_vocabulary_repository),
) -> list[VocabularyItem]:
    items = await vocabulary.list_by_level(level.value if level else None)
    return [vocabulary_to_public(item) for item in items]
