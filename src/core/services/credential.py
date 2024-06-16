from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import Credential
from src.core.services.service import Service

class CredentialService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Credential, db_session)