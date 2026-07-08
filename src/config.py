from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    first_superuser_email: str
    first_superuser_password: str
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
