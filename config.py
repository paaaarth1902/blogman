from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    database_url: str
    
    s3_bucket_name: str
    s3_region: str = "eu-north-1"
    s3_access_key_id: SecretStr | None = Field(
      default=None, validation_alias="aws_access_key_id"
  )
    s3_secret_access_key: SecretStr | None = Field(
      default=None, validation_alias="aws_secret_access_key"
  )
    s3_endpoint_url: str | None = None


    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_upload_size_bytes: int = 5 * 1024 * 1024
    posts_per_page: int = 10
    reset_token_expire_minutes: int = 30

    mail_server: str = "localhost" # SMTP server address
    mail_port: int = 587 # SMTP port - standard port
    mail_username: str = "" # SMTP username
    mail_password: SecretStr = SecretStr("") # SMTP password
    mail_from: str = "noreply@example.com" # Email sender address
    mail_use_tls: bool = True # Use TLS for email

    frontend_url: str = "http://localhost:8000"

settings = Settings()