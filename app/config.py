from pydantic import BaseModel
import os


class Settings(BaseModel):
    APP_NAME: str = "Library API"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://sa:123456@127.0.0.1:1430/LIBRARY?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=no&TrustServerCertificate=yes",
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()
