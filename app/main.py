from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import get_settings
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.characters import router as characters_router
from app.api.v1.creator import router as creator_router
from app.api.v1.chat import chat_router

from app.services.observability.trace import trace_middleware
from app.adapters.llm.base import NoOpLLM
from app.adapters.llm.openai_adapter import OpenAILLM


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.project_name, version=settings.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(trace_middleware)

    if settings.llm_provider == "openai" and settings.openai_api_key:
        print("Using OpenAI")
        app.state.llm = OpenAILLM(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            default_timeout_s=settings.llm_timeout_seconds,
        )
    else:
        print("Using NoOpLLM")
        app.state.llm = NoOpLLM()

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(characters_router, prefix=settings.api_v1_prefix)
    app.include_router(creator_router, prefix=settings.api_v1_prefix)
    app.include_router(chat_router, prefix=settings.api_v1_prefix)

    return app
