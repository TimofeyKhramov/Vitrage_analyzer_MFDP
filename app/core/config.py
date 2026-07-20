from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_host: str
    app_port: int
    debug: bool

    postgres_db: str
    postgres_user: str
    postgres_password: str
    database_url: str

    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_pass: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    upload_dir: str
    export_dir: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()