"""Script de inicialização do banco de dados"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import User, Person, MassSchedule, Mass, Scale, ScaleAssignment
from app.services.auth_service import get_user_by_username, create_user
from app.services.mass_service import get_mass_schedules, create_mass_schedule
from app.models.mass import DayOfWeek
from app.config import settings


def init_db():
    """Inicializa o banco de dados com dados padrão"""
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
    
    db = SessionLocal()
    try:
        # Criar admin inicial
        print("\nCriando usuário administrador...")
        if not get_user_by_username(db, settings.ADMIN_USERNAME):
            create_user(
                db,
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                full_name="Administrador",
                is_superuser=True
            )
            print(f"✓ Admin criado: {settings.ADMIN_USERNAME}")
        else:
            print(f"⚠ Admin já existe: {settings.ADMIN_USERNAME}")
        
        # Criar horários padrão
        print("\nCriando horários padrão...")
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
            
            print("✓ Horários padrão criados")
        else:
            print("⚠ Horários já existem")
        
        print("\n✅ Banco de dados inicializado com sucesso!")
        print(f"\nInformações de acesso:")
        print(f"  Usuário: {settings.ADMIN_USERNAME}")
        print(f"  Senha: {settings.ADMIN_PASSWORD}")
        print(f"\nExecute: uvicorn app.main:app --reload")
        
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
