"""Router de autenticação"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.services.auth_service import authenticate_user, create_user, get_user_by_username
from app.utils.security import create_access_token
from app.config import settings

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login e criação de token"""
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    """Logout"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    """Registrar novo usuário (apenas para desenvolvimento)"""
    # Em produção, remover ou proteger esta rota
    if get_user_by_username(db, username):
        raise HTTPException(
            status_code=400,
            detail="Usuário já existe"
        )
    
    user = create_user(db, username, email, password, full_name)
    return {"message": "Usuário criado com sucesso", "username": user.username}
