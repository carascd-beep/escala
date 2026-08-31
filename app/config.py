"""Configurações da aplicação"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente"""
    
    # Aplicação
    APP_NAME: str = "Escala Paróquia São João Bosco"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Segurança
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # Banco de Dados
    DATABASE_URL: str = "sqlite:///./data/escala.db"
    
    # Admin Inicial
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_EMAIL: str = "admin@paroquia.com"
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
