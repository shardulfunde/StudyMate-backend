from app.db.base import Base
# Import models to ensure metadata is populated without causing circular imports
from app.db import models  # noqa: F401,E402

__all__ = ["Base"]
