from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    navigator_api_key: SecretStr = Field(min_length=1)
    navigator_api_endpoint: str = Field(min_length=1)
    navigator_model: str = Field(min_length=1)
    openai_api_key: SecretStr = SecretStr("")
    decision_model: str = Field(default="gpt-6-luna", min_length=1)
    decision_timeout_seconds: float = Field(default=30, gt=0)
    tool_threshold: float = Field(default=0.5, gt=0, le=1)
