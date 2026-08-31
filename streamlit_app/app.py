import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="Escalas - Paróquia São João Bosco",
    page_icon="🙏",
    layout="wide"
)

st.title("📅 Escalas de Serviço - Paróquia São João Bosco")
st.caption("Sistema de escalas para Coroinhas, Acólitos e Cerimoniários")

# Configuração
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

# Sidebar
st.sidebar.title("📖 Menu")
page = st.sidebar.selectbox(
    "Navegar para:",
    ["📋 Todas as Escalas", "🗓️ Próximas Missas", "👤 Meus Coroinhas", "📊 Dashboard"]
)

if page == "📋 Todas as Escalas":
    st.header("Escalas Publicadas")
    
    try:
        response = requests.get(f"{BASE_URL}/api/escalas?published=true")
        if response.status_code == 200:
            escalas = response.json()
            
            if escalas:
                for escala in escalas:
                    st.subheader(f"Escala #{escala.get('id', 'N/A')} - {escala.get('mass_date', 'Sem data')}")
                    
                    if 'assignments' in escala and escala['assignments']:
                        df = pd.DataFrame(escala['assignments'])
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Escala sem atribuições ainda.")
            else:
                st.info("Nenhuma escala publicada no momento.")
        else:
            st.error(f"Erro ao buscar escalas: {response.status_code}")
    except Exception as e:
        st.error(f"Erro de conexão: {str(e)}")

elif page == "🗓️ Próximas Missas":
    st.header("Próximas Missas")
    try:
        response = requests.get(f"{BASE_URL}/api/missas")
        missas = response.json()
        
        if missas:
            df = pd.DataFrame(missas)
            df['date'] = pd.to_datetime(df['date']).dt.date
            df = df.sort_values('date')
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma missa cadastrada.")
    except Exception as e:
        st.error(f"Erro ao buscar missas: {str(e)}")

elif page == "👤 Meus Coroinhas":
    st.header("Meus Coroinhas")
    st.info("Em breve: lista personalizada de coroinhas por paróquia + status de disponibilidade.")

elif page == "📊 Dashboard":
    st.header("Dashboard Rápido")
    col1, col2, col3 = st.columns(3)
    
    try:
        response = requests.get(f"{BASE_URL}/api/escalas?published=true")
        escalas = response.json()
        col1.metric("Escalas Publicadas", len(escalas))
    except:
        col1.metric("Escalas Publicadas", "0")
    
    try:
        response = requests.get(f"{BASE_URL}/api/missas")
        missas = response.json()
        col2.metric("Missas Ativas", len(missas))
    except:
        col2.metric("Missas Ativas", "0")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pessoas")
        pessoas = response.json()
        col3.metric("Coroinhas Cadastrados", len(pessoas))
    except:
        col3.metric("Coroinhas Cadastrados", "0")
    
    st.caption("Dados atualizados automaticamente ao atualizar a página.")

# Footer
st.divider()
st.caption("Desenvolvido para a Paróquia São João Bosco | Versão MVP")
