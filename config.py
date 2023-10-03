from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    upload_file_path: str = 'upload_files/'
    model_config = SettingsConfigDict(env_file=".env")
    db_engine: str
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_pass: str


settings = Settings()
