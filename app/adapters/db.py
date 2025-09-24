from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
import ssl
import os
from app.settings import get_settings

_settings = get_settings()

_engine: Optional[AsyncEngine] = None
_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None


def _ssl_context() -> ssl.SSLContext | bool:
    ca = getattr(_settings, "db_ssl_root_cert", None)
    if ca:
        ctx = ssl.create_default_context(cafile=os.path.abspath(ca))
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx
    return True  # use system trust store


def get_engine() -> AsyncEngine:
    global _engine, _sessionmaker
    if _engine is None:
        _engine = create_async_engine(
            _settings.database_url,
            pool_pre_ping=True,
            connect_args={
                "ssl": _ssl_context(),
            },
        )
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global _sessionmaker
    if _sessionmaker is None:
        get_engine()
    assert _sessionmaker is not None
    async with _sessionmaker() as session:
        yield session
