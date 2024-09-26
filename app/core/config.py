from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env")

  UPLOAD_DIR: str = "uploads"
  DEFAULT_UPLOAD_SPEED: int = 1 * 1024 * 1024  # 1MB/s

settings = Settings()
