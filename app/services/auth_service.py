"""Serviço de autenticação"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import verify_password, get_password_hash
from typing import Optional


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Autentica usuário"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Busca usuário por username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca usuário por email"""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, email: str, password: str, full_name: str = None, is_superuser: bool = False) -> User:
    """Cria novo usuário"""
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_superuser=is_superuser
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
