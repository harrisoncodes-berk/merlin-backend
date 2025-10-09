import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.api.v1.creator import router, get_creator_repo
from app.domains.creator import Race, Class, Background, HitDice
from app.domains.character import Character


class _DummySession:
    async def commit(self):  # service may call commit()
        return None


class FakeCreatorRepo:
    def __init__(self):
        self.db_session = _DummySession()  # <-- give it a dummy async commit
        self._race = Race("race-1", "Elf", "Graceful", "Medium", 30, {"dex": 2}, [])
        self._class = Class(
            "class-1", "Wizard", "Arcane", 10, HitDice("d6", 1, 6), [], None, None, None
        )
        self._bg = Background("bg-1", "class-1", "Sage", "Scholar", [], [], [])
        self.created = None

    async def list_races(self):
        return [self._race]

    async def list_classes(self):
        return [self._class]

    async def list_backgrounds(self):
        return [self._bg]

    async def get_race(self, _):
        return self._race

    async def get_class(self, _):
        return self._class

    async def get_background(self, _):
        return self._bg

    async def create_character(self, user_id, character: Character):
        self.created = (user_id, character)
        return character


@pytest.mark.anyio
async def test_creator_endpoints_with_fake_repo():
    app = FastAPI()
    app.include_router(router)

    fake = FakeCreatorRepo()

    async def _override_repo():
        return fake

    app.dependency_overrides[get_creator_repo] = _override_repo

    # override auth
    from app.api.v1 import creator as creator_module

    async def _fake_user_id():
        return "user-1"

    app.dependency_overrides[creator_module.require_user_id] = _fake_user_id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.get("/creator/races")
        r2 = await ac.get("/creator/classes")
        r3 = await ac.get("/creator/backgrounds")
        assert r1.status_code == r2.status_code == r3.status_code == 200
        assert r1.json()[0]["name"] == "Elf"

        payload = {
            "name": "Awin",
            "classId": "class-1",
            "raceId": "race-1",
            "backgroundId": "bg-1",
            "skills": [],
            "weapons": [
                {
                    "id": "shortsword",
                    "name": "Shortsword",
                    "quantity": 1,
                    "weight": 2.0,
                    "description": "",
                }
            ],
            "spells": [],
            "abilities": {
                "str": 8,
                "dex": 14,
                "con": 10,
                "int": 16,
                "wis": 10,
                "cha": 8,
            },
        }
        resp = await ac.post("/creator/characters", json=payload)
        assert resp.status_code == 200, resp.text
        assert fake.created is not None
        user_id, ch = fake.created
        assert user_id == "user-1"
        assert ch.name == "Awin"
