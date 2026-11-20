import os


class Config:
    """Configuración leída desde variables de entorno (12-Factor: Config)."""

    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
