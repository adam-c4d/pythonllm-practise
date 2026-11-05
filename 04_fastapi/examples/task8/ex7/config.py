from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    shop_name: str = "Diamond Shop"
    api_key: str = "dev-secret"


settings = Settings()
