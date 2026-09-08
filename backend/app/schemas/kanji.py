from pydantic import BaseModel

from app.schemas.profile import JLPTLevel


class KanjiItem(BaseModel):
    id: str
    character: str
    onyomi: str
    kunyomi: str
    meaning: str
    level: JLPTLevel
    example_word: str | None = None
    example_reading: str | None = None
    example_meaning: str | None = None


def kanji_to_public(item: dict) -> KanjiItem:
    return KanjiItem(
        id=str(item["_id"]),
        character=item["character"],
        onyomi=item["onyomi"],
        kunyomi=item["kunyomi"],
        meaning=item["meaning"],
        level=item["level"],
        example_word=item.get("example_word"),
        example_reading=item.get("example_reading"),
        example_meaning=item.get("example_meaning"),
    )
