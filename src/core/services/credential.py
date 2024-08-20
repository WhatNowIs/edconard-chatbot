from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import Credential
from src.core.services.service import Service
from src.utils.logger import get_logger

class CredentialService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Credential, db_session)

    async def get_by_user_id(self, uid: str) -> Optional[Credential]:
        get_logger().info(f"Fetching credentials with user id: {uid}")
        result = await self.db_session.execute(select(Credential).filter(Credential.user_id == uid))
        return result.scalars().first()