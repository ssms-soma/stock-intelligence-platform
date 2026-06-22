from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "AI Stock Intelligence Platform"
    environment: str = "development"


settings = Settings()