"""Testes da API REST"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from datetime import date, timedelta


# Configurar banco de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Criar tabelas antes de cada teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestPessoasAPI:
    """Testes de Pessoas"""
    
    def test_create_person(self):
        """Testa criação de pessoa"""
        response = client.post("/api/pessoas", json={
            "full_name": "João da Silva",
            "display_name": "João",
            "server_type": "coroinha",
            "phone": "99999-9999"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["display_name"] == "João"
        assert data["server_type"] == "coroinha"
        assert data["is_active"] is True
    
    def test_list_persons(self):
        """Testa listagem de pessoas"""
        # Criar pessoa
        client.post("/api/pessoas", json={
            "full_name": "Maria Santos",
            "display_name": "Maria",
            "server_type": "acolito"
        })
        
        response = client.get("/api/pessoas")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_filter_persons_by_type(self):
        """Testa filtro por tipo"""
        client.post("/api/pessoas", json={
            "full_name": "Pedro Costa",
            "display_name": "Pedro",
            "server_type": "coroinha"
        })
        client.post("/api/pessoas", json={
            "full_name": "Ana Lima",
            "display_name": "Ana",
            "server_type": "cerimoniario"
        })
        
        response = client.get("/api/pessoas?server_type=coroinha")
        assert response.status_code == 200
        data = response.json()
        assert all(p["server_type"] == "coroinha" for p in data)
    
    def test_update_person(self):
        """Testa atualização completa de pessoa"""
        created = client.post("/api/pessoas", json={
            "full_name": "Pessoa Original",
            "display_name": "Original",
            "server_type": "coroinha",
            "experience": 1,
            "availability": "ambos",
        })
        person_id = created.json()["id"]

        response = client.put(f"/api/pessoas/{person_id}", json={
            "full_name": "Pessoa Atualizada",
            "display_name": "Atualizada",
            "server_type": "acolito",
            "experience": 3,
            "availability": "semana",
            "phone": "11999999999",
            "fixed_weekdays": [1, 4],
        })

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Pessoa Atualizada"
        assert data["display_name"] == "Atualizada"
        assert data["server_type"] == "acolito"
        assert data["experience"] == 3
        assert data["fixed_weekdays"] == [1, 4]

    def test_update_person_with_legacy_empty_availability(self):
        created = client.post("/api/pessoas", json={
            "full_name": "Pessoa Legada",
            "display_name": "Legada",
            "server_type": "coroinha",
        })
        person_id = created.json()["id"]
        response = client.put(f"/api/pessoas/{person_id}", json={"phone": "11988887777"})
        assert response.status_code == 200
        assert response.json()["phone"] == "11988887777"

    def test_deactivate_person(self):
        """Testa desativação de pessoa"""
        # Criar
        create_response = client.post("/api/pessoas", json={
            "full_name": "Carlos Souza",
            "display_name": "Carlos",
            "server_type": "coroinha"
        })
        person_id = create_response.json()["id"]
        
        # Desativar
        response = client.delete(f"/api/pessoas/{person_id}")
        assert response.status_code == 204
        
        # Verificar
        get_response = client.get(f"/api/pessoas/{person_id}")
        assert get_response.json()["is_active"] is False


class TestHorariosAPI:
    """Testes de Horários"""
    
    def test_create_schedule(self):
        """Testa criação de horário"""
        response = client.post("/api/horarios", json={
            "day_of_week": "monday",
            "time": "19:00",
            "description": "Missa Ordinária"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["day_of_week"] == "monday"
        assert data["time"] == "19:00"
    
    def test_list_schedules(self):
        """Testa listagem de horários"""
        client.post("/api/horarios", json={
            "day_of_week": "sunday",
            "time": "09:00"
        })
        
        response = client.get("/api/horarios")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestMissasAPI:
    """Testes de Missas"""
    
    def test_create_mass(self):
        """Testa criação de missa"""
        today = date.today()
        response = client.post("/api/missas", json={
            "date": today.isoformat(),
            "time": "19:00",
            "celebration": "Missa de Natal"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["time"] == "19:00"
    
    def test_generate_masses(self):
        """Testa geração de missas"""
        # Criar horário
        client.post("/api/horarios", json={
            "day_of_week": "monday",
            "time": "19:00"
        })
        
        # Gerar missas
        start = date.today()
        end = start + timedelta(days=7)
        response = client.post(f"/api/missas/gerar?start_date={start}&end_date={end}")
        assert response.status_code == 201
        assert "missas geradas" in response.json()["message"].lower()


class TestEscalasAPI:
    """Testes de Escalas"""
    
    def test_create_scale(self):
        """Testa criação de escala"""
        # Criar missa
        mass_response = client.post("/api/missas", json={
            "date": date.today().isoformat(),
            "time": "19:00"
        })
        mass_id = mass_response.json()["id"]
        
        # Criar escala
        response = client.post(f"/api/escalas/{mass_id}")
        assert response.status_code == 200
        assert response.json()["mass_id"] == mass_id
    
    def test_add_assignment(self):
        """Testa adicionar pessoa à escala"""
        # Criar pessoa
        person_response = client.post("/api/pessoas", json={
            "full_name": "João Teste",
            "display_name": "João",
            "server_type": "coroinha"
        })
        person_id = person_response.json()["id"]
        
        # Criar missa e escala
        mass_response = client.post("/api/missas", json={
            "date": date.today().isoformat(),
            "time": "19:00"
        })
        mass_id = mass_response.json()["id"]
        scale_response = client.post(f"/api/escalas/{mass_id}")
        scale_id = scale_response.json()["id"]
        
        # Adicionar atribuição
        response = client.post(f"/api/escalas/{scale_id}/atribuicoes", json={
            "person_id": person_id
        })
        assert response.status_code == 200
        assert response.json()["person_id"] == person_id
    
    def test_prevent_duplicate_assignment(self):
        """Testa prevenção de duplicidade"""
        # Criar pessoa
        person_response = client.post("/api/pessoas", json={
            "full_name": "Pedro Duplicado",
            "display_name": "Pedro",
            "server_type": "coroinha"
        })
        person_id = person_response.json()["id"]
        
        # Criar missa e escala
        mass_response = client.post("/api/missas", json={
            "date": date.today().isoformat(),
            "time": "19:00"
        })
        mass_id = mass_response.json()["id"]
        scale_response = client.post(f"/api/escalas/{mass_id}")
        scale_id = scale_response.json()["id"]
        
        # Adicionar primeira vez
        client.post(f"/api/escalas/{scale_id}/atribuicoes", json={
            "person_id": person_id
        })
        
        # Tentar adicionar novamente
        response = client.post(f"/api/escalas/{scale_id}/atribuicoes", json={
            "person_id": person_id
        })
        assert response.status_code == 400
        assert "já está escalada" in response.json()["detail"]
    
    def test_publish_scale(self):
        """Testa publicação de escala"""
        # Criar missa e escala
        mass_response = client.post("/api/missas", json={
            "date": date.today().isoformat(),
            "time": "19:00"
        })
        mass_id = mass_response.json()["id"]
        scale_response = client.post(f"/api/escalas/{mass_id}")
        scale_id = scale_response.json()["id"]
        
        # Publicar
        response = client.post(f"/api/escalas/{scale_id}/publicar")
        assert response.status_code == 200
        assert response.json()["published"] is True


class TestWebPages:
    """Testes de páginas web"""
    
    def test_home_page(self):
        """Testa página inicial"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Paróquia São João Bosco" in response.text
    
    def test_public_scale_page(self):
        """Testa página pública de escalas"""
        response = client.get("/escala")
        assert response.status_code == 200
        assert "Escala de Serviço" in response.text
    
    def test_login_page(self):
        """Testa página de login"""
        response = client.get("/login")
        assert response.status_code == 200
        assert "Entrar" in response.text
    
    def test_dashboard_requires_auth(self):
        """Testa que dashboard requer autenticação"""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_list_person_includes_cadastro_fields(self):
        client.post("/api/pessoas", json={
            "full_name": "Pessoa Cadastro",
            "display_name": "Pessoa",
            "server_type": "coroinha",
            "availability": "Todo Dia",
            "experience": 2,
        })
        response = client.get("/api/pessoas")
        assert response.status_code == 200
        assert response.json()[0]["availability"] == "ambos"
        assert response.json()[0]["experience"] == 2
