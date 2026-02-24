from app.schemas.roles import RoleAssignment
from app.schemas.scopes import ScopeAssignment
from app.schemas.programs import ProgramCreate, ProgramDelete
from app.schemas.years import YearCreate, YearDelete
from app.schemas.subjects import SubjectCreate, SubjectDelete, SubjectRejectRequest
from app.schemas.moderator_application import (
    ModeratorApplyRequest,
    ModeratorApplyResponse,
    ModeratorApplicationItem,
    ModeratorDecisionRequest,
    ModeratorDecisionResponse,
)
from app.schemas.resource_approval import ResourceRejectRequest

__all__ = [
    "RoleAssignment",
    "ScopeAssignment",
    "ProgramCreate",
    "ProgramDelete",
    "YearCreate",
    "YearDelete",
    "SubjectCreate",
    "SubjectDelete",
    "SubjectRejectRequest",
    "ModeratorApplyRequest",
    "ModeratorApplyResponse",
    "ModeratorApplicationItem",
    "ModeratorDecisionRequest",
    "ModeratorDecisionResponse",
    "ResourceRejectRequest",
]
