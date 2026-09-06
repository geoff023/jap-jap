from fastapi import APIRouter

from app.core.database import get_database

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Report API and database status. Never raises, even if MongoDB is down."""
    database_status = "unavailable"
    try:
        db = get_database()
        await db.command("ping")
        database_status = "connected"
    except Exception:
        database_status = "unavailable"

    return {"status": "ok", "database": database_status}
