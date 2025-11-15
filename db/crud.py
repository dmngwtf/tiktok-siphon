# db/crud.py
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select,func
from .models import UserVideo
from .database import AsyncSessionLocal

async def add_user_video(user_id: int, url: str, region: str | None = None, suffix: str | None = None):
    async with AsyncSessionLocal() as db:
        stmt = insert(UserVideo).values(
            user_id=user_id,
            url=url,
            region=region or "unknown",
            suffix=suffix  # ← СОХРАНЯЕМ
        )
        do_nothing_stmt = stmt.on_conflict_do_nothing(
            index_elements=['user_id', 'url']
        )
        await db.execute(do_nothing_stmt)
        await db.commit()

async def get_user_videos(user_id: int):
    """Возвращает список (url, suffix) от новых к старым"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserVideo.url, UserVideo.suffix)
            .where(UserVideo.user_id == user_id)
            .order_by(UserVideo.added_at.desc())
        )
        return result.all()  # ← [(url, suffix), ...]

async def get_users_by_url(url: str):
    """Возвращает список user_id, которые запрашивали видео"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(UserVideo.user_id).where(UserVideo.url == url))
        return result.scalars().all()
    
async def get_total_videos() -> int:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(UserVideo))
        return result.scalar_one()

async def get_region_stats() -> list[tuple[str, int]]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserVideo.region, func.count())
            .group_by(UserVideo.region)
            .order_by(func.count().desc())
        )
        return result.all()