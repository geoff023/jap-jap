from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_kanji_repository
from app.repositories.kanji_repository import KanjiRepository
from app.schemas.kanji import KanjiItem, kanji_to_public
from app.schemas.profile import JLPTLevel

router = APIRouter()


@router.get("", response_model=list[KanjiItem])
async def list_kanji(
    level: JLPTLevel | None = None,
    current_user: dict = Depends(get_current_user),
    kanji: KanjiRepository = Depends(get_kanji_repository),
) -> list[KanjiItem]:
    items = await kanji.list_by_level(level.value if level else None)
    return [kanji_to_public(item) for item in items]
