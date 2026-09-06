from pydantic import BaseModel

from app.schemas.profile import JLPTLevel


class GrammarConcept(BaseModel):
    id: str
    key: str
    title: str
    level: JLPTLevel
    explanation: str
    example_sentence: str
    example_translation: str
    answer: str


def grammar_to_public(item: dict) -> GrammarConcept:
    return GrammarConcept(
        id=str(item["_id"]),
        key=item["key"],
        title=item["title"],
        level=item["level"],
        explanation=item["explanation"],
        example_sentence=item["example_sentence"],
        example_translation=item["example_translation"],
        answer=item["answer"],
    )
