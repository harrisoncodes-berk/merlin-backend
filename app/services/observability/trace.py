import uuid
from fastapi import Request


def new_trace_id() -> str:
    return uuid.uuid4().hex


async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id") or new_trace_id()
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response
