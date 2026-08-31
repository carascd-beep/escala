"""Aplicação principal FastAPI"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import api, web, auth
from pathlib import Path

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de gerenciamento de escalas para coroinhas, acólitos e cerimoniários",
    version="1.0.0"
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluir routers
app.include_router(auth.router)
app.include_router(api.router)
app.include_router(web.router)


@app.on_event("startup")
async def startup_event():
    """Inicialização do banco de dados"""
    from app.database import engine, Base, ensure_schema
    from app.models import User, Person, MassSchedule, Mass, Scale, ScaleAssignment
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    
    # Criar admin inicial se não existir
    from app.database import SessionLocal
    from app.services.auth_service import get_user_by_username, create_user
    
    db = SessionLocal()
    try:
        from app.services.cadastro_service import import_cadastro_if_empty
        cadastro_path = Path(__file__).parents[1] / "docs" / "CadastroCoroinhas.xlsx"
        imported = import_cadastro_if_empty(db, cadastro_path) if cadastro_path.exists() else 0
        if imported:
            print(f"Cadastro inicial importado: {imported} pessoas")
        if not get_user_by_username(db, settings.ADMIN_USERNAME):
            create_user(
                db,
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                full_name="Administrador",
                is_superuser=True
            )
            print(f"Admin inicial criado: {settings.ADMIN_USERNAME}")
        
        # Criar horários padrão se não existirem
        from app.models.mass import MassSchedule, DayOfWeek
        from app.services.mass_service import get_mass_schedules, create_mass_schedule
        
        if not get_mass_schedules(db):
            # Segunda a Sexta: 19:00
            for day in [DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
                       DayOfWeek.THURSDAY, DayOfWeek.FRIDAY]:
                create_mass_schedule(db, day, "19:00")
            
            # Sábado: 14:00 e 18:00
            create_mass_schedule(db, DayOfWeek.SATURDAY, "14:00")
            create_mass_schedule(db, DayOfWeek.SATURDAY, "18:00")
            
            # Domingo: 07:00, 09:00, 17:30, 19:30
            create_mass_schedule(db, DayOfWeek.SUNDAY, "07:00")
            create_mass_schedule(db, DayOfWeek.SUNDAY, "09:00")
            create_mass_schedule(db, DayOfWeek.SUNDAY, "17:30")
            create_mass_schedule(db, DayOfWeek.SUNDAY, "19:30")
            
            print("Horários padrão criados")
    finally:
        db.close()


@app.get("/")
async def root():
    """Redireciona para página inicial"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")
