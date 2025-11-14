# db/crud.py
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from .models import UserVideo
from .database import AsyncSessionLocal

async def add_user_video(user_id: int, url: str, region: str | None = None):
    async with AsyncSessionLocal() as db:
        stmt = insert(UserVideo).values(
            user_id=user_id,
            url=url,
            region=region or "unknown"
        )

        # ← ПРАВИЛЬНО: PostgreSQL upsert
        do_nothing_stmt = stmt.on_conflict_do_nothing(
            index_elements=['user_id', 'url']
        )
        await db.execute(do_nothing_stmt)
        await db.commit()

async def get_users_by_url(url: str):
    """Возвращает список user_id, которые запрашивали видео"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(UserVideo.user_id).where(UserVideo.url == url))
        return result.scalars().all()