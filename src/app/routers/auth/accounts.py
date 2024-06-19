from typing import Any
from fastapi import APIRouter, Depends, HTTPException, logger
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST
from src.core.services.mail import EmailTemplateService, EmailTypeService, ResendClient, get_mail_service
from src.core.services.otp import OTPService
from src.core.services.user import UserService
from src.core.dbconfig.postgres import get_db
from src.core.models.base import OTP, EmailTemplate, EmailType, EntityStatus, User
from src.schema import EmailTypeEnum, ResetPassword, UserCreateModel, UserModel, VerifyOtp
from src.utils.logger import get_logger 

accounts_router = APIRouter()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

def get_otp_service(db: AsyncSession = Depends(get_db)) -> OTPService:
    return OTPService(db)

@accounts_router.post("/create", response_model=UserModel)
async def create_user(
    data: UserCreateModel,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    mail_client: ResendClient = Depends(get_mail_service)
) -> Any:
    try:
        user_in = User(**data.user_data.dict())
        user = await user_service.create(user_in, data.password)
    except Exception as e:
        get_logger().error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

    try:
        email_type_service = EmailTypeService(db)
        email_template_service = EmailTemplateService(db)

        email_type: EmailType = await email_type_service.get_email_type_by_name(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
        email_template: EmailTemplate = await email_template_service.get_template_by_name(EmailTypeEnum.ACCOUNT_VERIFICATION.value)
    
        otp_service = OTPService(db)
        otp = OTP(
            email=user.email,
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
            "expiry_minutes": 10
        }

        email_content = ResendClient.render_template(email_template.content, context)

        mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)

        return UserModel(**user.to_dict())
    except Exception as e:
        get_logger().error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")


# @accounts_router.post("/update", response_model=UserModel)
# async def update_user(
#     data: UserModel,
#     db: AsyncSession = Depends(get_db),
#     user_service: UserService = Depends(get_user_service)
# ) -> Any:
#     try:
#         user_in = User(**data.user_data.dict())
#         user = await user_service.create(user_in, data.password)
#     except Exception as e:
#         get_logger().error(f"Error creating user: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error while creating user")

#     return UserModel(**user.to_dict())


@accounts_router.post("/signin")
async def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    is_authenticated = await user_service.login(form_data.username, form_data.password)
    if not is_authenticated:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    return JSONResponse(
        status_code=200,
        content={"message": "Login successful"}
    )

@accounts_router.post("/verify-otp/{otp_type}")
async def verify_otp_code(
    data: VerifyOtp,
    db: AsyncSession = Depends(get_db),
    otp_service: OTPService = Depends(get_otp_service),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    try:
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
            raise HTTPException(status_code=500, detail="Your one-time password has already been used")        
        elif(otp.is_expired()):
            otp.status = EntityStatus.Inactive
            raise HTTPException(status_code=500, detail="Your one-time password has expired")
        else:            
            otp.status = EntityStatus.Used
            
            await otp_service.update(otp.id, otp)
        
        return {"message": "OTP verified successfully"}
        
    except Exception as e:
        get_logger().error(f"Error verifying otp: {e}")
        raise HTTPException(status_code=500, detail=f"Error verifying otp: {e}")
    
    


@accounts_router.post("/reset-password")
async def reset_password(
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
    
        otp = OTP(
            email=user.email,
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
            "expiry_minutes": 10
        }

        email_content = ResendClient.render_template(email_template.content, context)

        mail_client.send_email(content=email_content, subject=email_template.subject, to_email=user.email)

        return {"message": "An email with 6 OTP Digits has been sent to your email address"}
        
    except Exception as e:
        get_logger().error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying your account")
    