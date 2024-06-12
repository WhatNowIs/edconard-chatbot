from sqlalchemy.ext.asyncio import AsyncSession as Session
from common.models.base import Credential
from common.services.service import Service

class CredentialService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Credential, db_session)