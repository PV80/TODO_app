"""PropOps AI (Kenya Edition) backend service."""

from typing import TYPE_CHECKING

from .database import initialize_database
from .service import PropOpsService

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .webapp import create_app as _create_app

__all__ = ["initialize_database", "PropOpsService", "create_app"]


def __getattr__(name: str):
    if name == "create_app":
        from .webapp import create_app as _create_app

        return _create_app
    raise AttributeError(name)
