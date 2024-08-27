import os
from typing import List, Optional, Tuple
from distutils.util import strtobool
from create_llama.backend.app.utils.helpers import Article
import jwt
import json
from sqlalchemy.future import select
from pydantic import parse_obj_as
from src.core.models.base import EntityStatus, Message, Role, User, Credential, UserRole, Workspace
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.orm import selectinload
from src.core.services.service import Service
from src.core.services.credential import CredentialService
from src.utils import datetime_to_str
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
        self.db_session.add(user_in)
        await self.db_session.commit()
        await self.db_session.refresh(user_in)
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
        self.db_session.add(credential)
        await self.db_session.commit()
        await self.db_session.refresh(credential)
        self.logger.info(f"Created credentials for user with id: {user_in.id}")

        return user_in
    
    
    async def create_default_super_admin_account_if_not_exists(self, user: User, password: str) -> Tuple[User, bool]:
        self.logger.info(f"Creating default super admin")

        try:
            role = await self.db_session.execute(
                select(Role).filter(Role.name == UserRole.SUPER_ADMIN.value)
            )
            role = role.scalar_one_or_none()

            default_super_admin = await self.db_session.execute(
                select(User).filter(User.email == user.email)
            )
            default_super_admin = default_super_admin.scalar_one_or_none()

            if not default_super_admin:
                default_super_admin = user
                default_super_admin.role_id = role.id
                default_super_admin = await self.create(default_super_admin, password)
                return default_super_admin, True

            else:
                self.logger.info(f"Default super admin account already exists")

            return default_super_admin, False

        except Exception as e:
            self.logger.error(f"Error creating default super admin account: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        self.logger.info(f"Fetching user with email: {email}")
        result = await self.db_session.execute(
            select(User)
            .options(selectinload(User.role)) 
            .filter(User.email == email)
        )
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

            if user.status == EntityStatus.Active:

                token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                refresh_token_expires = timedelta(minutes = REFRESH_TOKEN_EXPIRE_MINUTES)

                token = self.create_access_token(
                    data = { 
                        "sub": user.id, 
                        "email": user.email,
                        "role": user.role.name
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
            else:               

                 False, None, None, None, "Your account is not active please contact the adminitrator to activate your account"
            
        self.logger.warning(f"User login failed for email: {email}")

        return False, None, None, None, "Your email or password is incorrect"

    async def update_chat_mode(self, user_id: str, is_research_or_exploration: bool, redis_client: Redis) -> None:
        self.logger.info(f"Updating chat mode for user ID: {user_id} to {is_research_or_exploration}")
        # Update the chat mode in Redis without expiration
        value = str(is_research_or_exploration)
        await redis_client.set(f"chat_mode:{user_id}", value=value)
        self.logger.info(f"Chat mode for user ID: {user_id} updated successfully")

    async def update_article(self, user_id: str, article: Article, redis_client: Redis):
        self.logger.info(f"Updating article for user ID: {user_id}")
        try:
            # Serialize the Pydantic object to a JSON string
            article_json = article.model_dump_json()

            # Update the article in Redis without expiration
            update_status = await redis_client.set(f"article:{user_id}", article_json)
            if update_status:
                self.logger.info(f"Article for user ID: {user_id} updated successfully")
                self.logger.debug(f"Updated article data: {article_json}")
            else:
                self.logger.error(f"Failed to update article for user ID: {user_id}")
                return None

            # Verify the update
            stored_article_json = await redis_client.get(f"article:{user_id}")
            if stored_article_json != article_json:
                self.logger.error(f"Mismatch detected! Retrieved article data doesn't match the updated data for user ID: {user_id}")
                return None
            
            self.logger.info(stored_article_json)

            return Article.model_validate_json(stored_article_json)
        except Exception as e:
            self.logger.exception(f"An error occurred while updating article for user ID: {user_id}: {e}")
            return None

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
    
    async def update_chat_history(self, user_id: str, chat_history: List[Message], redis_client: Redis) -> None:
        self.logger.info(f"Updating chat history for user ID: {user_id}")
        # Serialize the Pydantic object to a JSON string
        chat_history_json = json.dumps([message.to_dict() for message in chat_history],  default=datetime_to_str)
        # Update the chat history in Redis without expiration
        await redis_client.set(f"chat_history:{user_id}", chat_history_json)
        self.logger.info(f"Chat history for user ID: {user_id} updated successfully")

    async def get_chat_history(self, user_id: str, redis_client: Redis):
        self.logger.info(f"Retrieving chat history for user ID: {user_id}")
        # Retrieve the JSON string from Redis
        chat_history_json = await redis_client.get(f"chat_history:{user_id}")
        if chat_history_json is None:
            self.logger.info(f"No chat history found for user ID: {user_id}")
            return None
        # Deserialize the JSON string back to a list of ChatMessage objects
        chat_history = json.loads(chat_history_json)
        # chat_history = parse_obj_as(List[Message], chat_history_dicts)
        self.logger.info(f"Chat history for user ID: {user_id} retrieved successfully")
        return chat_history
    
    async def get_chat_mode(self, user_id: str, redis_client: Redis) -> Optional[bool]:
        self.logger.info(f"Retrieving chat mode for user ID: {user_id}")
        # Retrieve the chat mode from Redis
        chat_mode = await redis_client.get(f"chat_mode:{user_id}")
        if chat_mode is None:
            self.logger.warning(f"No chat mode found for user ID: {user_id}")
            return None
        else:
            chat_mode = strtobool(chat_mode)
            self.logger.info(f"Chat mode for user ID: {user_id} is {chat_mode}")
            return bool(chat_mode)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None, secret_key: str = SECRET_KEY):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str):
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = datetime.fromtimestamp(decoded_token["exp"])
            return decoded_token if exp >= datetime.utcnow() else None
        except jwt.PyJWTError:
            return None
        

    async def change_password(self, user: User, current_password: str, new_password: str) -> Tuple[bool, str]:
        self.logger.info(f"Password change attempt for user with email: {user.email}")

        if not await self.verify_user_password(user.id, current_password):
            self.logger.warning(f"Current password for user with email {user.email} is incorrect")
            return False, "Current password is incorrect"

        hashed_password, salt = encrypt(new_password)

        # async with self.db_session as session:
        result = await self.db_session.execute(select(Credential).filter(Credential.user_id == user.id))
        credential = result.scalars().first()
        if credential:
            credential.password = hashed_password
            credential.salt = salt
            credential.updated_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(credential)
            self.logger.info(f"Password updated successfully for user with email: {user.email}")
            return True, "Password updated successfully"

        self.logger.error(f"Failed to update password for user with email: {user.email}")
        return False, "Failed to update password"
    
    
    async def deactivate_user(self, user_id: str, block_user: bool) -> Tuple[bool, User]:
        self.logger.info(f"Deactivating user with id: {user_id}")
        # async with self.db_session as session:
        result = await self.db_session.execute(
            select(User)
            .options(selectinload(User.role))
            .filter(User.id == user_id)
        )
        user = result.scalars().first()
        if user:
            user.status = EntityStatus.Blocked if block_user else EntityStatus.Active
            user.updated_at = datetime.utcnow()

            await self.db_session.commit()
            await self.db_session.refresh(user)

            self.logger.info(f"User (de)activated successfully")

            return block_user, user
        

        self.logger.error(f"Failed to deactivated for user with user id: {user_id}")
        return block_user, user

    
    async def update_user_role(self, user_id: str, role_name: str) -> Tuple[bool, str]:
        self.logger.info(f"Updating user role with id: {user_id}")
        # async with self.db_session as session:
        
        role = await self.db_session.execute(
            select(Role).filter(Role.name == role_name)
        )
        role = role.scalar_one_or_none()

        result = await self.db_session.execute(
            select(User)
            .options(selectinload(User.role))
            .filter(User.id == user_id)
        )
        user = result.scalars().first()
        if user:
            user.role = role
            user.role_id = role.id
            user.updated_at = datetime.utcnow()

            await self.db_session.commit()
            await self.db_session.refresh(user)

            self.logger.info(f"User role updated successfully")

            return user        

        self.logger.error(f"Failed to deactivated for user with user id: {user_id}")
        return user
    
    async def get_all_workspace_users(self, exclude_user_id: str, workspace_id: str) -> List[User]:
        self.logger.info(f"Fetching all users except user with id: {exclude_user_id} and user who are not in workspace id: {workspace_id}")
        try:
            # Get users that are not in the specified workspace and not the excluded user
            result = await self.db_session.execute(
                select(User)
                .options(selectinload(User.role))
                .options(selectinload(User.workspaces))
                .filter(User.id != exclude_user_id)
                .filter(~User.workspaces.any(Workspace.id == workspace_id))
            )
            users = result.scalars().all()
            self.logger.info(f"Fetched {len(users)} users excluding user id: {exclude_user_id} and not in workspace id: {workspace_id}")
            return users
        except Exception as e:
            self.logger.error(f"Error fetching users: {e}")
            raise

    
    async def get_all_users(self, exclude_user_id: str) -> List[User]:
        self.logger.info(f"Fetching all users except user with id: {exclude_user_id}")
        try:
            # Get users that are not in the specified workspace and not the excluded user
            result = await self.db_session.execute(
                select(User)
                .options(selectinload(User.role))
                .filter(User.id != exclude_user_id)
            )
            users = result.scalars().all()
            self.logger.info(f"Fetched {len(users)} users excluding user id: {exclude_user_id}")
            return users
        except Exception as e:
            self.logger.error(f"Error fetching users: {e}")
            raise


    async def get_user(self, user_id: str) -> User:
        self.logger.info(f"Fetching user with id: {user_id}")
        try:
            # Get users that are not in the specified workspace and not the excluded user
            result = await self.db_session.execute(
                select(User)
                .options(selectinload(User.role))
                .filter(User.id == user_id)
            )
            user = result.scalars().first()
            self.logger.info(f"Fetched user with id: {user_id}")
            return user
        except Exception as e:
            self.logger.error(f"Error fetching users: {e}")
            raise




async def create_default_super_admin_account(user_service: UserService, user: User) -> Tuple[User, bool] :
    return await user_service.create_default_super_admin_account_if_not_exists(user)