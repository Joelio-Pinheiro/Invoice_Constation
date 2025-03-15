from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DRIVE_FOLDER_ID: str
    CREDENTIALS_FILE: str
    
    class Config:
        env_file = ".env" 

settings = Settings()