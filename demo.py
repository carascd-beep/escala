"""Script de demonstração - Cria escala de exemplo"""
import requests
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

def demo():
    print("=" * 60)
    print("DEMONSTRAÇÃO - Sistema de Escalas")
    print("=" * 60)
    
    # 1. Listar pessoas
    print("\n1. Pessoas cadastradas:")
    response = requests.get(f"{BASE_URL}/api/pessoas")
    persons = response.json()
    for p in persons:
        print(f"   - {p['display_name']} ({p['server_type']})")
    
    # 2. Listar missas
    print("\n2. Missas geradas (próximos 7 dias):")
    start = date.today()
    end = start + timedelta(days=7)
    response = requests.get(f"{BASE_URL}/api/missas", params={
        "start_date": start.isoformat(),
        "end_date": end.isoformat()
    })
    masses = response.json()
    for m in masses[:5]:
        print(f"   - {m['date']} às {m['time']}")
    
    # 3. Criar escala para primeira missa
    if masses:
        mass_id = masses[0]['id']
        print(f"\n3. Criando escala para missa ID {mass_id}:")
        
        # Criar escala
        response = requests.post(f"{BASE_URL}/api/escalas/{mass_id}")
        scale = response.json()
        scale_id = scale['id']
        print(f"   ✓ Escala criada (ID: {scale_id})")
        
        # Adicionar pessoas
        if persons:
            for person in persons[:3]:
                response = requests.post(
                    f"{BASE_URL}/api/escalas/{scale_id}/atribuicoes",
                    json={"person_id": person['id']}
                )
                if response.status_code == 200:
                    print(f"   ✓ {person['display_name']} adicionado à escala")
        
        # Publicar escala
        response = requests.post(f"{BASE_URL}/api/escalas/{scale_id}/publicar")
        if response.status_code == 200:
            print(f"   ✓ Escala publicada!")
    
    # 4. Visualizar escala pública
    print("\n4. Acessando página pública:")
    print(f"   URL: {BASE_URL}/escala")
    
    # 5. Documentação API
    print("\n5. Documentação da API:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    
    print("\n" + "=" * 60)
    print("✅ Demonstração concluída!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Acesse http://localhost:8000")
    print("2. Faça login: admin / admin123")
    print("3. Gerencie pessoas, horários e escalas")
    print("4. Visualize escalas públicas em /escala")

if __name__ == "__main__":
    demo()
