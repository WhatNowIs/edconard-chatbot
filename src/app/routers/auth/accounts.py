
import jwt
from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, logger, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.services.role import RoleService
from src.core.services.workspace import WorkspaceService
from starlette.status import HTTP_400_BAD_REQUEST
from src.core.config.redis import get_redis_client
from src.core.services.credential import CredentialService
from src.core.services.mail import EmailTemplateService, EmailTypeService, ResendClient, get_mail_service
from src.core.services.otp import OTPService
from src.core.services.user import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_SECRET_KEY, UserService
from src.core.config.postgres import get_db
from src.core.models.base import OTP, EmailTemplate, EmailType, EntityStatus, OTPGenerator, User, UserRole, get_otp_expiration
from src.schema import ChangePassword, DeactivateResponse, EmailTypeEnum, RefreshBody, ResetPassword, UpdatePassword, UpdateUserRole, UserCreateModel, UserModel, VerifyOtp
from src.utils.encryption import encrypt, to_base64
from src.utils.logger import get_logger 
from redis.asyncio.client import Redis

accounts_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    return WorkspaceService(db)

def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db)

async def get_session(
    token: str = Depends(oauth2_scheme), 
    user_service: UserService = Depends(get_user_service),
    redis_client: Redis = Depends(get_redis_client)
) -> Optional[dict]:
    
    payload = user_service.decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Retrieve session from Redis
    session_data = redis_client.get(f"session:{payload['sub']}")
    if session_data:
        get_logger().info(session_data)
        return user_service.decode_access_token(token)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session not found",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_otp_service(db: AsyncSession = Depends(get_db)) -> OTPService:
    return OTPService(db)

def get_credential_service(db: AsyncSession = Depends(get_db)) -> CredentialService:
    return CredentialService(db)

@accounts_router.get("/me")
async def get_me(
    session: dict = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    if "sub" in session:
        user_id = session["sub"]

        user = await user_service.get_user(user_id)

        return UserModel(**user.to_dict())
    
    return {"message": "Not authenticated"}

@accounts_router.post("/create", response_model=UserModel)
async def create_user(
    data: UserCreateModel,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    mail_client: ResendClient = Depends(get_mail_service),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    role_service: RoleService = Depends(get_role_service)
) -> Any:
    try:
        role = await role_service.get_role_by_name(UserRole.USER.value)
        user_in = User(**data.user_data.dict())
        user_in.role_id = role.id
        user_in.role = role

        user = await user_service.create(user_in, data.password)
        workspace = await workspace_service.create_default_workspace_if_not_exists(user)
        
        email_type_service = EmailTypeService(db)
        email_template_service = EmailTemplateService(db)

        email_type: EmailType = await email_type_service.get_email_type_by_name(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
        email_template: EmailTemplate = await email_template_service.get_template_by_name(EmailTypeEnum.ACCOUNT_VERIFICATION.value)

    
        otp_service = OTPService(db)
        code = OTPGenerator().generate_unique_otp()
        otp = OTP(
            email=user.email,
            user_id=user.id,
            email_template_id=email_template.id,
            email_type_id=email_type.id,
            status=EntityStatus.Active,
            code=code,
            created_at=datetime.now(),
            expires_at=get_otp_expiration()
        )
        await otp_service.create(otp)
        await workspace_service.add_user_to_workspace(workspace.id, user.id)
        await workspace_service.db_session.commit()

        # Define the context for the email template
        context = {
            "username": user.email,
            "code": otp.code,
            "expiry_minutes": 10,
            "uid": to_base64(user.email),
            "verification_type": to_base64(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
        }

        email_content = ResendClient.render_template(email_template.content, context)

        await mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)


        return UserModel(**user.to_dict())
    except Exception as e:
        get_logger().error(f"Error has occured: {e}")
        raise HTTPException(status_code=500, detail=f"Error has occured: {e}")

@accounts_router.post("/signin")
async def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),    
    redis_client: Redis = Depends(get_redis_client)
):
    is_authenticated, token, refresh_token, user, message = await user_service.login(
        form_data.username, 
        form_data.password, 
        redis_client, 
        True
    )
    if not is_authenticated:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    return {
        "access_token": token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer", 
        "user": UserModel(**user.to_dict()), 
        "message": message
    }

@accounts_router.post("/refresh")
async def refresh_token(
    data: RefreshBody,
    user_service: UserService = Depends(get_user_service),
    redis_client: Redis = Depends(get_redis_client)
):
    try:
        payload = jwt.decode(data.refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        user_id = payload["sub"]
        email = payload["email"]

        # Verify the refresh token is stored in Redis
        stored_refresh_token = await redis_client.get(f"refresh_session:{user_id}")
        if stored_refresh_token != data.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = user_service.create_access_token({"sub": user_id, "email": email}, token_expires)

        await redis_client.setex(f"session:{user_id}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, new_access_token)

        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )



@accounts_router.post("/verify-otp")
async def verify_otp_code(
    data: VerifyOtp,
    db: AsyncSession = Depends(get_db),
    otp_service: OTPService = Depends(get_otp_service),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    try:
        get_logger().info(data)
        user = await user_service.get_by_email(data.email)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating user")

    try:
        otp_service = OTPService(db)
        otp = await otp_service.get_otp_by_user_email_code(user.id, user.email, data.code)

        if otp is None:
            raise HTTPException(status_code=404, detail="OTP not found")
        
        if(otp.status == EntityStatus.Used):
            return { "message": "Your one-time password has already been used", "status": 400 }
        elif(otp.is_expired()):
            otp.status = EntityStatus.Inactive
            return { "message": "Your one-time password has expired", "status": 400 }
        else:            
            otp.status = EntityStatus.Used
            await otp_service.update(id=otp.id, obj_in=otp)

            if(data.otp_type == EmailTypeEnum.ACCOUNT_VERIFICATION.value):
                user.status = EntityStatus.Active
                await user_service.update(id=user.id, obj_in=user)

                return { "message": "Account verified successfully", "status": 200 }
        
        return { "message": "OTP verified successfully", "status": 200 }
        
    except Exception as e:
        get_logger().error(f"Error verifying otp: {e}")

        return {"message": str(e), "status": 400}
    
@accounts_router.get("/resend-otp/{uid}")
async def resend_otp_code(
    uid: str,
    db: AsyncSession = Depends(get_db),
    otp_service: OTPService = Depends(get_otp_service),
    mail_client: ResendClient = Depends(get_mail_service),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    try:
        otp_service = OTPService(db)
        email_type_service = EmailTypeService(db)
        email_template_service = EmailTemplateService(db)
        otp = await otp_service.get_otp_by_email(uid)
        email_template: EmailTemplate = await email_template_service.get_template_by_name(EmailTypeEnum.ACCOUNT_VERIFICATION.value)

        if(otp is not None):
            context = {
                "username": otp.email,
                "code": otp.code,
                "expiry_minutes": 10,
                "uid": to_base64(otp.email),
                "verification_type": to_base64(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
            }
            email_content = ResendClient.render_template(email_template.content, context)
            await mail_client.send_email(content=email_content, subject=email_template.subject, to_email=otp.email)
            
            return {"message": "An email with 6 OTP Digits has been sent to your email address", "status": 200}

        email_type: EmailType = await email_type_service.get_email_type_by_name(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
    
        otp_service = OTPService(db)
        user = await user_service.get_by_email(uid)
        otp = OTP(
            email=uid,
            user_id=user.id,
            email_template_id=email_template.id,
            email_type_id=email_type.id,
            status=EntityStatus.Active
        )
        await otp_service.create(otp)

        # Define the context for the email template
        context = {
            "username": user.email,
            "code": otp.code,
            "expiry_minutes": 10,
            "uid": to_base64(user.email),
            "verification_type": to_base64(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
        }

        email_content = ResendClient.render_template(email_template.content, context)

        await mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)
        
        return {"message": "An email with 6 OTP Digits has been sent to your email address", "status": 200}
        
    except Exception as e:
        get_logger().error(f"Error verifying otp: {e}")

        return {"message": str(e), "status": 400}

@accounts_router.post("/forgot-password")
async def forgot_password(
    data: ResetPassword,
    db: AsyncSession = Depends(get_db),
    otp_service: OTPService = Depends(get_otp_service),
    user_service: UserService = Depends(get_user_service),
    mail_client: ResendClient = Depends(get_mail_service)
) -> Any:
    try:
        user = await user_service.get_by_email(data.email)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating user")

    try:
        
        email_type_service = EmailTypeService(db)
        email_template_service = EmailTemplateService(db)

        email_type: EmailType = await email_type_service.get_email_type_by_name(EmailTypeEnum.RESET_PASSWORD.value)
        email_template: EmailTemplate = await email_template_service.get_template_by_name(EmailTypeEnum.RESET_PASSWORD.value)

        otp_service = OTPService(db)
        code = OTPGenerator().generate_unique_otp()
    
        otp = OTP(
            email=user.email,
            user_id=user.id,
            email_template_id=email_template.id,
            email_type_id=email_type.id,
            status=EntityStatus.Active,
            code=code,
            created_at=datetime.now(),
            expires_at=get_otp_expiration()
        )
        await otp_service.create(otp)

        # Define the context for the email template
        context = {
            "username": user.email,
            "expiry_minutes": 10,
            "uid": to_base64(user.email),
            "code": otp.code,
            "verification_type": to_base64(EmailTypeEnum.RESET_PASSWORD.value)
        }

        email_content = ResendClient.render_template(email_template.content, context)

        await mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)

        return {"message": "An email with a reset link has been sent to your email address", "status": 200}
        
    except Exception as e:
        get_logger().error(f"Error sending email: {e}")

        return {"message": str(e), "status": 400}
    
@accounts_router.post("/reset-password")
async def reset_password(
    data: UpdatePassword,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    credential_service: CredentialService = Depends(get_credential_service),
    mail_client: ResendClient = Depends(get_mail_service)
) -> Any:
    try:
        user = await user_service.get_by_email(data.email)

        if (user is not None):

            credential = await credential_service.get_by_user_id(user.id)
            hashed_password, salt = encrypt(data.password)
            credential.password = hashed_password
            credential.salt = salt

            await credential_service.update(id=credential.id, obj_in=credential)

            email_template_service = EmailTemplateService(db)
            email_template: EmailTemplate = await email_template_service.get_template_by_name(EmailTypeEnum.PASSWORD_UPDATE.value)
            context = {
                "username": user.email
            }
            email_content = ResendClient.render_template(email_template.content, context)

            await mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)


            return {"message": "Your password been updated successfully", "status": 200}
        
        return {"message": "No account linked with the email you provided", "status": 400}
    except Exception as e:
        get_logger().error(f"Error sending email: {e}")
        return {"message": str(e), "status": 400}  
    
@accounts_router.post("/change-password")
async def change_password(
    data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(get_session), 
    user_service: UserService = Depends(get_user_service),
    mail_client: ResendClient = Depends(get_mail_service)
) -> Any:
    try:
        
        if "sub" in session:
            email = session["email"]
            user = await user_service.get_by_email(email)

            if (user is not None):

                is_updated, _ = await user_service.change_password(user=user, current_password=data.current_password, new_password=data.new_password)

                if(is_updated):

                    email_template_service = EmailTemplateService(db)
                    email_template: EmailTemplate = await email_template_service.get_template_by_name(EmailTypeEnum.PASSWORD_UPDATE.value)
                    context = {
                        "username": user.email
                    }
                    email_content = ResendClient.render_template(email_template.content, context)

                    await mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)

                    return {"message": "Your password been updated successfully", "status": 200}
                else:
                    return {"message": "Failed to update password", "status": 400}
            
            return {"message": "No account linked with the email you provided", "status": 400}
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        get_logger().error(f"Error sending email: {e}")
        return {"message": str(e), "status": 400}
    
@accounts_router.get("", response_model=List[UserModel])
async def get_all_users(
    session: dict = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    # Check if the user is authenticated and has the necessary permissions (optional)
    if "sub" in session:
        try:
            users = await user_service.get_all_users(session['sub'])
            return [UserModel(**user.to_dict()) for user in users]
        except Exception as e:
            get_logger().error(f"Error retrieving users: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving users")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )

    
@accounts_router.get("/{user_id}/deactivate/{block_user}", response_model=DeactivateResponse)
async def deactivate_user_account(
    user_id: str,
    block_user: bool,
    session: dict = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    # Check if the user is authenticated and has the necessary permissions (optional)
    if "sub" in session:
        try:
            if session['role'] == UserRole.SUPER_ADMIN.value:
                block_user, user = await user_service.deactivate_user(user_id, block_user)
                return DeactivateResponse(
                    block_user = block_user,
                    data = UserModel(**user.to_dict())
                )
            else:
                return DeactivateResponse(
                    block_user=block_user,
                    data = None
                )
        except Exception as e:
            get_logger().error(f"Error retrieving users: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving users")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
@accounts_router.patch("/{user_id}/role", response_model=UserModel | None)
async def update_user_role(
    user_id: str,
    data: UpdateUserRole,
    session: dict = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    # Check if the user is authenticated and has the necessary permissions (optional)
    if "sub" in session:
        try:
            if session['role'] == UserRole.SUPER_ADMIN.value:
                user = await user_service.update_user_role(user_id, data.role)
                return user
            else:
                return None
            
        except Exception as e:
            get_logger().error(f"Error retrieving users: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving users")
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )

@accounts_router.get("/users/{workspace_id}", response_model=List[UserModel])
async def get_all_workspace_users(
    workspace_id: str,
    session: dict = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    # Check if the user is authenticated and has the necessary permissions (optional)
    if "sub" in session:
        try:
            users = await user_service.get_all_workspace_users(session['sub'], workspace_id)
            return [UserModel(**user.to_dict()) for user in users]
        except Exception as e:
            get_logger().error(f"Error retrieving users: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving users")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )


@accounts_router.get("/signout")
async def signout(
    session: dict = Depends(get_session), 
    redis_client: Redis = Depends(get_redis_client)
):
    if "sub" in session:
        user_id = session["sub"]
        # Remove the session from Redis
        await redis_client.delete(f"session:{user_id}")
        await redis_client.delete(f"refresh_session:{user_id}")
        await redis_client.delete(f"chat_mode:{user_id}")
        
        return JSONResponse(status_code=200, content={"message": "Successfully signed out"})
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )
