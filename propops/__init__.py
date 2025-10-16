"""PropOps AI (Kenya Edition) backend service."""

from .database import initialize_database
from .service import PropOpsService

__all__ = ["initialize_database", "PropOpsService"]
