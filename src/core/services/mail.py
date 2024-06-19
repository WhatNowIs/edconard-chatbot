import os
from typing import Optional, TypeVar
import resend
from jinja2 import Template
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import EmailTemplate, EmailType
from src.llm.env_config import EnvConfig, get_config
from src.core.services.service import Service
from src.core.models.base import Base
from src.schema import EmailTypeEnum

env_config = get_config()

resend.api_key = env_config.resend_api_key


T = TypeVar('T', bound=Base)

class ResendClient:
    def __init__(self, env_config: EnvConfig):
        self.from_email = env_config.from_email
        
    @classmethod    
    def render_template(cls, template_str: str, context: dict) -> str:
        template = Template(template_str)
        return template.render(context)
    
    async def send_email(self, to_email: str, subject: str, content: str):   
        params: resend.Emails.SendParams = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "html": content,
        }

        response = resend.Emails.send(params)
        return response


class EmailTemplateService(Service):
    def __init__(self, db_session: Session):
        super().__init__(EmailTemplate, db_session)
    
    async def get_template_by_name(self, template_name: str) -> Optional[EmailTemplate]:
        result = await self.db_session.execute(
            select(EmailTemplate).filter(EmailTemplate.name == template_name)
        )
        return result.scalars().first()

    def convert_snake_case_to_title(self, snake_case_string):
        words = snake_case_string.split('_')
        title_string = ' '.join(word.capitalize() for word in words)
        return title_string

    async def populate_email_templates(self, templates_dir: str):
        template_files = os.listdir(templates_dir)

        for template_file in template_files:
            template_name, _ = os.path.splitext(template_file)

            
            result = await self.db_session.execute(
                select(EmailTemplate).filter(EmailTemplate.name == template_name)
            )
            existing_email_template = result.scalars().first()

            if not existing_email_template:
                with open(os.path.join(templates_dir, template_file), 'r') as file:
                    content = file.read()
                    new_email_template = EmailTemplate(
                        name=template_name,
                        subject=f"{self.convert_snake_case_to_title(template_name)}",
                        content=content
                    )
                    self.db_session.add(new_email_template)

        await self.db_session.commit()
        

class EmailTypeService(Service):
    def __init__(self, db_session: Session):
        super().__init__(EmailType, db_session)
    
    async def get_email_type_by_name(self, email_type: str) -> Optional[EmailType]:
        result = await self.db_session.execute(
            select(EmailType).filter(EmailType.type == email_type)
        )
        return result.scalars().first()
    
    async def populate_email_types(self):
        for email_type in EmailTypeEnum:
            result = await self.db_session.execute(
                select(EmailType).filter(EmailType.type == email_type.value)
            )
            existing_email_type = result.scalars().first()
            if not existing_email_type:
                new_email_type = EmailType(type=email_type.value)
                self.db_session.add(new_email_type)
                
        await self.db_session.commit()

resend_client = ResendClient(env_config)


def get_mail_service():
    global resend_client

    return resend_client

