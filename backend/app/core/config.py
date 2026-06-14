from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Q&A Assistant"
    debug: bool = True

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ai_qa_assistant"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_max_tokens: int = 4096
    deepseek_temperature: float = 0.7

    rate_limit_per_minute: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
