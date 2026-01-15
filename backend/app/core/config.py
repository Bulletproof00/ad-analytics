from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    meta_access_token: str | None = None
    meta_api_version: str = "v24.0"
    meta_base_url: str = "https://graph.facebook.com"

    db_host: str = "postgres"
    db_user: str = "adradar"
    db_pass: str = "adradar"
    db_name: str = "adradar"

    basic_auth_user: str = "admin"
    basic_auth_pass: str = "admin"

    default_country: str = "DE"
    default_since_days: int = 90
    max_results_per_keyword: int = 2000
    rate_limit_max_retries: int = 5
    rate_limit_base_sleep_ms: int = 500
    redis_url: str = "redis://redis:6379/0"
    llm_api_key: str | None = None

    class Config:
        env_prefix = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}/{self.db_name}"
        )


settings = Settings()
