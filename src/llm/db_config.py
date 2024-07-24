from pydantic import Field, BaseModel

class DBConfig(BaseModel):
    db_uri: str | None = Field(
        default=None,
        description="The url to connect to the database which will be used to store all related user conversations",
        env="DB_URI"
    )
    redis_url: str | None = Field(
        default=None,
        description="The url to connect to the database which will be used to store all related user conversations",
        env="REDIS_URL"
    )
