from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_grammar_repository
from app.repositories.grammar_repository import GrammarRepository
from app.schemas.grammar import GrammarConcept, grammar_to_public
from app.schemas.profile import JLPTLevel

router = APIRouter()


@router.get("", response_model=list[GrammarConcept])
async def list_grammar(
    level: JLPTLevel | None = None,
    current_user: dict = Depends(get_current_user),
    grammar: GrammarRepository = Depends(get_grammar_repository),
) -> list[GrammarConcept]:
    items = await grammar.list_by_level(level.value if level else None)
    return [grammar_to_public(item) for item in items]
