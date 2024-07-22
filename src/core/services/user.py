import os
from typing import Optional, Tuple
from create_llama.backend.app.utils.helpers import Article
import jwt
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.future import select
from src.core.models.base import User, Credential
from src.core.services.service import Service
from src.core.services.credential import CredentialService
from src.utils.encryption import encrypt, verify
from src.utils.logger import get_logger
import uuid
from datetime import datetime, timedelta
from redis.asyncio.client import Redis

SECRET_KEY = "CE586DECFCBF526AFA26846516E9F" 
REFRESH_SECRET_KEY = "qkM3CsTaKd2vMOzb4RiKE9LaDaQqZiZU"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
REFRESH_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES * 7

class UserService(Service):
    def __init__(self, db_session: Session):
        super().__init__(User, db_session)
        self.credential_service = CredentialService(db_session)
        self.logger = get_logger()

    async def create(self, user_in: User, password: str) -> User:
        self.logger.info(f"Creating a new user with first name: {user_in.first_name}")
        user_in.created_at = datetime.utcnow()
        async with self.db_session as session:
            session.add(user_in)
            await session.commit()
            await session.refresh(user_in)
        self.logger.info(f"Created user with id: {user_in.id}")

        self.logger.info(f"Creating credentials for user with id: {user_in.id}")
        hashed_password, salt = encrypt(password)
        credential = Credential(
            id=str(uuid.uuid4()),
            user_id=user_in.id,
            password=hashed_password,
            salt=salt,
            created_at=datetime.utcnow(),
            status='Active'
        )
        async with self.db_session as session:
            session.add(credential)
            await session.commit()
            await session.refresh(credential)
        self.logger.info(f"Created credentials for user with id: {user_in.id}")

        return user_in

    async def get_by_email(self, email: str) -> Optional[User]:
        self.logger.info(f"Fetching user with email: {email}")
        async with self.db_session as session:
            result = await session.execute(select(User).filter(User.email == email))
            return result.scalars().first()

    async def verify_user_password(self, user_id: str, password: str) -> bool:
        self.logger.info(f"Verifying password for user with id: {user_id}")
        user_credential = await self.credential_service.get_by_user_id(user_id)
        if user_credential:
            is_valid = verify(password, user_credential.password, user_credential.salt)
            if is_valid:
                self.logger.info(f"Password verification successful for user with id: {user_id}")
            else:
                self.logger.warning(f"Password verification failed for user with id: {user_id}")
            return is_valid
        self.logger.warning(f"User with id: {user_id} not found for password verification")
        return False

    async def login(
        self,
        email: str, 
        password: str, 
        redis_client: Redis, 
        is_research_or_exploration: bool
    ) -> Tuple[bool, Optional[str],  Optional[User], str]:
        
        self.logger.info(f"User login attempt with email: {email}")
        user = await self.get_by_email(email)
        
        if user and await self.verify_user_password(user.id, password):
            self.logger.info(f"User login successful for email: {email}")

            token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(minutes = REFRESH_TOKEN_EXPIRE_MINUTES)

            token = self.create_access_token(
                data = { 
                    "sub": user.id, 
                    "email": user.email
                }, 
                expires_delta = token_expires
            )

            refresh_token = self.create_access_token(
                data = { 
                    "sub": user.id, 
                    "email": user.email
                }, 
                expires_delta = refresh_token_expires, 
                secret_key = REFRESH_SECRET_KEY
            )

            await redis_client.setex(
                f"session:{user.id}", 
                ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
                token
            )
            await redis_client.setex(
                f"refresh_session:{user.id}", 
                REFRESH_TOKEN_EXPIRE_MINUTES * 60, 
                refresh_token
            )
            # Store the chat mode information
            await redis_client.setex(
                f"chat_mode:{user.id}", 
                ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
                str(is_research_or_exploration)
            )

            return True, token, refresh_token, user, "Login successfully"
            
        self.logger.warning(f"User login failed for email: {email}")

        return False, None, None, None, "Your email or password is incorrect"

    async def update_chat_mode(self, user_id: str, is_research_or_explorationde: bool, redis_client: Redis) -> None:
        self.logger.info(f"Updating chat mode for user ID: {user_id} to {is_research_or_explorationde}")
        # Update the chat mode in Redis without expiration
        await redis_client.set(f"chat_mode:{user_id}", value=str(is_research_or_explorationde))
        self.logger.info(f"Chat mode for user ID: {user_id} updated successfully")

    async def update_article(self, user_id: str, article: Article, redis_client: Redis) -> None:
        self.logger.info(f"Updating current article for user ID: {user_id}")
        # Serialize the Pydantic object to a JSON string
        article_json = article.model_dump_json()
        # Update the chat mode in Redis without expiration
        await redis_client.set(f"article:{user_id}", article_json)
        self.logger.info(f"Chat mode for user ID: {user_id} updated successfully")

    async def get_article(self, user_id: str, redis_client: Redis) -> Article:
        self.logger.info(f"Retrieving current article for user ID: {user_id}")
        # Retrieve the JSON string from Redis
        article_json = await redis_client.get(f"article:{user_id}")
        if article_json is None:
            self.logger.info(f"No article found for user ID: {user_id}")
            return None
        # Deserialize the JSON string back to the Pydantic object
        article = Article.model_validate_json(article_json)
        self.logger.info(f"Article for user ID: {user_id} retrieved successfully")
        return article
    
    async def get_chat_mode(self, user_id: str, redis_client: Redis) -> Optional[str]:
        self.logger.info(f"Retrieving chat mode for user ID: {user_id}")
        # Retrieve the chat mode from Redis
        chat_mode = await redis_client.get(f"chat_mode:{user_id}")
        if chat_mode is None:
            self.logger.warning(f"No chat mode found for user ID: {user_id}")
        else:
            self.logger.info(f"Chat mode for user ID: {user_id} is {chat_mode}")
        return chat_mode
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str):
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = datetime.fromtimestamp(decoded_token["exp"])
            return decoded_token if exp >= datetime.utcnow() else None
        except jwt.PyJWTError:
            return None
