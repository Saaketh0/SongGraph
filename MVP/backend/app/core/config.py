from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Music Graph Backend", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/songgraph",
        alias="DATABASE_URL",
    )
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    read_from_stage: bool = Field(default=False, alias="READ_FROM_STAGE")
    search_result_limit: int = Field(default=20, alias="SEARCH_RESULT_LIMIT")
    graph_node_cap: int = Field(default=1000, alias="GRAPH_NODE_CAP")
    artist_seed_cap: int = Field(default=300, alias="ARTIST_SEED_CAP")
    genre_seed_sample_size: int = Field(default=50, alias="GENRE_SEED_SAMPLE_SIZE")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
