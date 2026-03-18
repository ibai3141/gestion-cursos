import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

class Settings:
    # SupabaseCD
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
    MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
    MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common")
    MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI")
    MICROSOFT_SCOPES = os.getenv(
        "MICROSOFT_SCOPES",
        "openid profile email User.Read"
    )
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        origins = [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)

        return origins

settings = Settings()
