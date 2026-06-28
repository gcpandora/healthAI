from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "dev_key"
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"
    hf_token: str = ""
    hf_model: str = "google/vit-base-patch16-224"
    mock_hf: bool = False
    backend_url: str = "http://api:8000"
    cache_ttl: int = 300
    cache_maxsize: int = 500
    rate_limit: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
