from typing import List
from ipaddress import IPv4Address
from pydantic import SecretStr, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    title: str = "Smart U"
    description: str = 'API-documentation "Smart U" API'
    version: str = "0.0.1"

    # allow_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]

    database: str
    database_driver: SecretStr
    database_user: SecretStr
    database_password: SecretStr
    database_host: SecretStr
    database_port: Secret[int]
    database_name: SecretStr

    database_engine_echo: bool = False
    database_engine_future: bool = True
    database_engine_pool_size: int = 5
    database_engine_max_overflow: int = 10
    database_engine_pool_timeout: int = 30
    database_engine_pool_recycle: int = 1800
    database_engine_pool_pre_ping: bool = True

    database_session_autoflush: bool = False
    database_session_expire_on_commit: bool = False


settings = Settings()  # type: ignore
