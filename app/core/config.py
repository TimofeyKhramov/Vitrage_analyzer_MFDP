from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


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
    rabbitmq_password: str
    rabbitmq_queue: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    upload_dir: str
    export_dir: str

    project_dir: Path = Path(__file__).resolve().parents[2]

    storage_dir: Path = project_dir / "storage" / "processing"

    models_dir: Path = project_dir / "app" / "core" / "models_yolo"

    drawings_model_path: Path = models_dir / "no_generate_data640.pt"

    doors_model_path: Path = models_dir / "doors_otr.pt"

    conf_drawings: float = 0.3

    imgsz: int = 640

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()