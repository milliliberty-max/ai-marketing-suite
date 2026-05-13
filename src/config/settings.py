from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Instagram Graph API
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""

    # OpenAI
    openai_api_key: str = ""

    # Groq
    groq_api_key: str = ""

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    upload_dir: str = "./uploads"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
