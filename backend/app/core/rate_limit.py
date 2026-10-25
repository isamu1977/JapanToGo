"""Rate limiting primitives backed by ``slowapi``."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

#: Shared limiter instance. The storage is in-memory, which is enough for the
#: single-instance Coolify deployment.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.rate_limit_storage_uri,
    enabled=settings.rate_limit_enabled,
    headers_enabled=True,
)


def rate_limit(limit_value: Any) -> Callable[[Callable], Callable]:
    """Apply a ``slowapi`` limit to a FastAPI endpoint.

    ``slowapi`` wraps the endpoint in a function defined inside its own
    module. When the endpoint uses ``from __future__ import annotations``,
    FastAPI would then resolve the (stringified) parameter annotations
    against *slowapi's* namespace and lose the ``Depends(...)`` metadata,
    turning body parameters into query parameters.

    Copying the **resolved** signature onto the wrapper keeps every
    annotation intact.
    """

    def decorator(func: Callable) -> Callable:
        wrapper = limiter.limit(limit_value)(func)
        wrapper.__signature__ = inspect.signature(func, eval_str=True)  # type: ignore[attr-defined]
        return wrapper

    return decorator


__all__ = ["limiter", "rate_limit"]
