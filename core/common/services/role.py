from sqlalchemy.ext.asyncio import AsyncSession as Session
from common.models.base import Role
from common.services.service import Service

class RoleService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Role, db_session)