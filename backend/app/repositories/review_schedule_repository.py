from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

# SM-2-inspired spaced repetition, adapted for binary correct/incorrect
# grading rather than Anki's 0-5 recall-quality scale (this app has no such
# rating anywhere) — see docs/PROJECT_STATE.md's Phase 12 section for the
# full rationale behind this simplification.
DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
EASE_DELTA_CORRECT = 0.1
EASE_DELTA_INCORRECT = -0.2

# A concept with no schedule document has never been reviewed at all —
# treat it as more overdue than anything with a real due date, however old.
# Naive (no tzinfo) to match what Motor/PyMongo hands back for stored BSON
# datetimes by default — comparing a naive and an aware datetime raises.
UNSEEN_SORT_KEY = datetime.min


class ReviewScheduleRepository:
    """Tracks per-(user, category, concept) spaced-repetition state — when a
    concept is next "due" for review. This is a scheduling signal only,
    entirely separate from learner_skills' mastery tracking (Phase 5):
    mastery answers "how well do you know this," due_at answers "when
    should you see this again." Both are updated from the same answer
    event, by different repositories, for different purposes.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["review_schedule"]

    async def record_review(
        self, user_id: str, category: str, concept: str, correct: bool, when: datetime
    ) -> None:
        existing = await self._collection.find_one(
            {"user_id": user_id, "category": category, "concept": concept}
        )
        ease_factor = existing["ease_factor"] if existing else DEFAULT_EASE_FACTOR
        repetitions = existing["repetitions"] if existing else 0
        interval_days = existing["interval_days"] if existing else 0

        if correct:
            repetitions += 1
            ease_factor = max(MIN_EASE_FACTOR, ease_factor + EASE_DELTA_CORRECT)
            if repetitions == 1:
                interval_days = 1
            elif repetitions == 2:
                interval_days = 6
            else:
                interval_days = round(interval_days * ease_factor)
        else:
            repetitions = 0
            ease_factor = max(MIN_EASE_FACTOR, ease_factor + EASE_DELTA_INCORRECT)
            interval_days = 1

        due_at = when + timedelta(days=interval_days)

        await self._collection.update_one(
            {"user_id": user_id, "category": category, "concept": concept},
            {
                "$set": {
                    "ease_factor": ease_factor,
                    "interval_days": interval_days,
                    "repetitions": repetitions,
                    "due_at": due_at,
                    "last_reviewed_at": when,
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "category": category,
                    "concept": concept,
                    "created_at": when,
                },
            },
            upsert=True,
        )

    async def due_dates_by_concept(self, user_id: str, category: str) -> dict[str, datetime]:
        """A concept absent from the returned dict has never been reviewed —
        callers should treat that as maximally overdue (see UNSEEN_SORT_KEY)."""
        cursor = self._collection.find({"user_id": user_id, "category": category})
        docs = await cursor.to_list(length=None)
        return {doc["concept"]: doc["due_at"] for doc in docs}

    async def ensure_indexes(self) -> None:
        await self._collection.create_index(
            [("user_id", 1), ("category", 1), ("concept", 1)], unique=True
        )
        await self._collection.create_index("user_id")
