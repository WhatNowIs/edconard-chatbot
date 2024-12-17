
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel

class MailConfig(BaseModel):
    resend_api_key: str | None = Field(
        default=None,
        description="API key for sending emails using resend",
        env="RESEND_API_KEY"
    )
    from_email: str | None = Field(
        default=None,
        description="Master email from where the email need to be sent from",
        env="FROM_EMAIL"
    )

class BaseEnvConfig(BaseModel):
    # Env for topic generation    
    gcp_scopes: str | None = Field(
        default=None,
        description="Google cloud scopes we need to use for access the document",
        env="GCP_SCOPES",
    )
    topics_speadsheet_url: str | None = Field(
        default=None,
        description="The url to the predefined topics used for classification",
        env="TOPICS_SPREADSHEET_URL",
    )
    sheets_names: str | None = Field(
        default=None,
        description="Contains all the predefined sheets we need",
        env="SHEETS_NAMES",
    )


    
