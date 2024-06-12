from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.future import select
from common.models.base import User, Credential
from common.services.service import Service
from common.services.credential import CredentialService
from common.utils.encryption import encrypt, verify
from common.utils.logger import get_logger
import uuid
from datetime import datetime

class UserService(Service):
    def __init__(self, db_session: Session):
        super().__init__(User, db_session)
        self.credential_service = CredentialService(db_session)
        self.logger = get_logger()

    async def create(self, user_in: User, password: str) -> User:
        self.logger.info(f"Creating a new user with first name: {user_in.first_name}")
        user_in.id = uuid.uuid4()
        user_in.created_at = datetime.utcnow()
        async with self.db_session() as session:
            session.add(user_in)
            await session.commit()
            await session.refresh(user_in)
        self.logger.info(f"Created user with id: {user_in.id}")

        self.logger.info(f"Creating credentials for user with id: {user_in.id}")
        hashed_password, salt = encrypt(password)
        credential = Credential(
            id=uuid.uuid4(),
            user_id=user_in.id,
            password=hashed_password,
            salt=salt,
            created_at=datetime.utcnow(),
            status='Active'
        )
        await self.credential_service.create(credential)
        self.logger.info(f"Created credentials for user with id: {user_in.id}")

        return user_in

    async def get_by_email(self, email: str) -> Optional[User]:
        self.logger.info(f"Fetching user with email: {email}")
        async with self.db_session() as session:
            result = await session.execute(select(User).filter(User.email == email))
            return result.scalars().first()

    async def verify_user_password(self, user_id: uuid.UUID, password: str) -> bool:
        self.logger.info(f"Verifying password for user with id: {user_id}")
        user_credential = await self.credential_service.get(user_id)
        if user_credential:
            is_valid = verify(password, user_credential.password, user_credential.salt)
            if is_valid:
                self.logger.info(f"Password verification successful for user with id: {user_id}")
            else:
                self.logger.warning(f"Password verification failed for user with id: {user_id}")
            return is_valid
        self.logger.warning(f"User with id: {user_id} not found for password verification")
        return False

    async def login(self, email: str, password: str) -> bool:
        self.logger.info(f"User login attempt with email: {email}")
        user = await self.get_by_email(email)
        if user and await self.verify_user_password(user.id, password):
            self.logger.info(f"User login successful for email: {email}")
            return True
        self.logger.warning(f"User login failed for email: {email}")
        return False