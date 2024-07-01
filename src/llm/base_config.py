
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
    aws_key: str | None = Field(
        default=None,
        description="The key to authenticate to aws.",
        env="AWS_KEY",
    )
    aws_secret: str | None = Field(
        default=None,
        description="The secret used to authenticate to aws.",
        env="AWS_SECRET",
    )
    s3_region: str | None = Field(
        default=None,
        description="The region where the bucket is located and data is stored.",
        env="S3_REGION",
    )
    s3_bucket_name: str | None = Field(
        default=None,
        description="The name of the bucket holding our data.",
        env="S3_BUCKET_NAME",
    )
    s3_asset_bucket_name: str | None = Field(
        default=None,
        description="The bucket that contains the assets.",
        env="S3_ASSET_BUCKET_NAME",
    )
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


    
