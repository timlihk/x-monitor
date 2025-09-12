import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    X_API_KEY = os.getenv("X_API_KEY")
    X_API_SECRET = os.getenv("X_API_SECRET") 
    X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
    X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")  # or "deepseek-reasoner"
    
    DB_URL = os.getenv("DB_URL", "sqlite:///./local.db")
    
    SCHEDULER_TIMEZONE = "UTC"
    DAILY_RUN_HOUR = 8
    DAILY_RUN_MINUTE = 0