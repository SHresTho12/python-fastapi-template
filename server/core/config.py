# import os
#
# import pytz
# from dotenv import load_dotenv
#
# # Load environment variables from .env file
# load_dotenv()
#
#
# class Config:
#     """Central configuration for the """
#     # Load environment variables
#     MONGO_URL = os.getenv("MONGO_URL")
#     ORIGINS = os.getenv("ORIGINS", "").split(",")
#     OPEN_AI_API_KEY = os.getenv('OPENAI_API_KEY')
#     COHERE_API_KEY = os.getenv('COHERE_API_KEY')
#     LOCAL_TIMEZONE = pytz.timezone(os.getenv('LOCAL_TIMEZONE', 'Asia/Dhaka'))
#     API_KEY = os.getenv("API_KEY")
#     ADMIN_AUTH = os.getenv("ADMIN_AUTH")
#     S3_BUCKET = os.environ['S3_BUCKET']
#     AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
#     AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
#     AWS_REGION = os.environ['AWS_REGION']
#
#
# config = Config()


from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Any
import pytz
from functools import lru_cache

class Config(BaseSettings):
    """Central configuration for the server using Pydantic."""
    mongo_url: str
    openai_api_key: str
    cohere_api_key: str
    # local_timezone: str | Any
    api_key: str
    admin_auth: str
    s3_bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    origins: List[HttpUrl] = Field(default_factory=list)

    refresh_token_expire: int
    access_token_expire: int

    access_token_secret_key: str
    refresh_token_secret_key: str
    jwt_algorithm: str

    super_admin_email: str
    super_admin_password: str

    # # Timezone Validator: Convert the string to a pytz.timezone object
    # @field_validator('local_timezone', mode='before')
    # def convert_to_timezone(cls, v):
    #     """Convert the string to a valid pytz timezone object."""
    #     # if v not in pytz.all_timezones:
    #     #     raise ValueError(f'{v} is not a valid timezone')
    #     return pytz.timezone(v)  # Convert the string to pytz.timezone object

    # Origins Validator: Splitting the comma-separated origins
    @field_validator('origins', mode='before')
    def split_origins(cls, v):
        """Split comma-separated string into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Caching the config object with lru_cache to load only once
@lru_cache()
def get_config() -> Config:
    return Config()