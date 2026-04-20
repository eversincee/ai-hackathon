from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./passports.db"
    scan_storage_dir: str = "./scans"
    feedback_log_path: str = "./feedback.jsonl"
    ocr_url: str = "http://localhost:8001"
    vlm_url: str = "http://localhost:11434"
    llm_url: str = "http://localhost:11434"
    vlm_model: str = "qwen2.5vl:3b"
    llm_model: str = "qwen2.5:7b-instruct"


settings = Settings()
