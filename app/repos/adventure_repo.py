from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.adventures import Adventure, AdventureStatus
from app.models.adventure_tables import adventures


class AdventureRepo:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def list_adventures(self) -> list[Adventure]:
        stmt = select(adventures)
        res = await self.db_session.execute(stmt)
        rows = res.mappings().all()
        return [_row_to_adventure(r) for r in rows]


def _row_to_adventure(row: dict) -> Adventure:
    return Adventure(
        adventure_id=str(row["adventure_id"]),
        title=row["title"],
        story_brief=row["story_brief"],
        starting_status=AdventureStatus(**row["starting_status"]),
    )
