from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DEBUG: bool = True
    DB_NAME: str = 'postgres'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = '3803'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    SECRET_KEY: str | None = None

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379


CONFIG = Config()
