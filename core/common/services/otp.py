from sqlalchemy.ext.asyncio import AsyncSession as Session
from common.models.base import OTP
from common.services.service import Service

class OTPService(Service):
    def __init__(self, db_session: Session):
        super().__init__(OTP, db_session)