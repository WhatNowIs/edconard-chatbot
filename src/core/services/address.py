from sqlalchemy.ext.asyncio import AsyncSession as Session
from models.base import Address
from services.service import Service

class AddressService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Address, db_session)