from sqlalchemy.ext.asyncio import AsyncSession as Session
from common.models.base import Tenant
from common.services.service import Service

class TenantService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Tenant, db_session)