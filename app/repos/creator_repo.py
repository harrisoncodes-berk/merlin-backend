from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import races
from app.schemas.creator import Race


def _race_row_to_out(row: dict) -> Race:
    return Race(
        id=str(row["id"]),
        name=row["name"],
        description=row["description"],
        size=row["size"],
        speed=row["speed"],
        abilityBonuses=row["ability_bonuses"] or {},
        features=row["features"] or [],
    )


async def list_races(session: AsyncSession) -> list[Race]:
    stmt = select(
        races.c.id,
        races.c.name,
        races.c.description,
        races.c.size,
        races.c.speed,
        races.c.ability_bonuses,
        races.c.features,
    )
    res = await session.execute(stmt)
    rows = res.mappings().all()
    return [_race_row_to_out(r) for r in rows]
