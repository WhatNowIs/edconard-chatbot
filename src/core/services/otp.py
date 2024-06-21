from typing import Optional
from fastapi import logger
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import OTP, EntityStatus
from src.core.services.service import Service

class OTPService(Service):
    def __init__(self, db_session: Session):
        super().__init__(OTP, db_session)

    async def get_otp_by_user_email_code(self, user_id: str, email: str, code: str) -> Optional[OTP]:
        try:
            result = await self.db_session.execute(
                select(OTP).filter(OTP.user_id == user_id, OTP.email == email, OTP.code == code)
                .options(
                    joinedload(OTP.email_type)
                )
            )
            otp = result.scalars().first()
            return otp
        except Exception as e:
            logger.error(f"Error fetching OTP: {e}")
            return None
        
    async def get_otp_by_email(self, email: str) -> Optional[OTP]:
        try:
            result = await self.db_session.execute(
                select(OTP).filter(OTP.email == email, OTP.status == EntityStatus.Active, OTP.expires_at < datetime.now())
                .options(
                    joinedload(OTP.email_type)
                )
            )
            otp = result.scalars().first()
            return otp
        except Exception as e:
            logger.error(f"Error fetching OTP: {e}")
            return None


