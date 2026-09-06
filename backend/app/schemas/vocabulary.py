from pydantic import BaseModel

from app.schemas.profile import JLPTLevel


class VocabularyItem(BaseModel):
    id: str
    term: str
    reading: str
    meaning: str
    level: JLPTLevel
    example_sentence: str | None = None
    example_translation: str | None = None


def vocabulary_to_public(item: dict) -> VocabularyItem:
    return VocabularyItem(
        id=str(item["_id"]),
        term=item["term"],
        reading=item["reading"],
        meaning=item["meaning"],
        level=item["level"],
        example_sentence=item.get("example_sentence"),
        example_translation=item.get("example_translation"),
    )
