import os
from datetime import date, timedelta

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Escalas - Paróquia São João Bosco",
    page_icon="🙏",
    layout="wide",
)

st.title("📅 Escalas de Serviço - Paróquia São João Bosco")
st.caption("Sistema de escalas para Coroinhas, Acólitos e Cerimoniários")

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def get_period() -> tuple[date, date]:
    start = date.today()
    return start, start + timedelta(days=31)


def get_json(path: str, **params):
    response = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.sidebar.title("📖 Menu")
page = st.sidebar.selectbox(
    "Navegar para:",
    ["📋 Todas as Escalas", "🗓️ Próximas Missas", "👤 Meus Coroinhas", "📊 Dashboard"],
)

if page == "📋 Todas as Escalas":
    st.header("Escalas Publicadas")
    try:
        start_date, end_date = get_period()
        escalas = get_json(
            "/api/escalas",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        escalas = [escala for escala in escalas if escala.get("published") is True]
        if escalas:
            for escala in escalas:
                mass = escala.get("mass") or {}
                st.subheader(
                    f"Escala #{escala.get('id', 'N/A')} - "
                    f"{mass.get('date', 'Sem data')} {mass.get('time', '')}"
                )
                assignments = escala.get("assignments", [])
                if assignments:
                    st.dataframe(pd.DataFrame(assignments), use_container_width=True, hide_index=True)
                else:
                    st.info("Escala sem atribuições ainda.")
        else:
            st.info("Nenhuma escala publicada no momento.")
    except requests.RequestException as exc:
        st.error(f"Erro de conexão com a API ({BASE_URL}): {exc}")

elif page == "🗓️ Próximas Missas":
    st.header("Próximas Missas")
    try:
        start_date, end_date = get_period()
        missas = get_json(
            "/api/missas",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        if missas:
            df = pd.DataFrame(missas)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date
                df = df.sort_values("date")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma missa cadastrada.")
    except requests.RequestException as exc:
        st.error(f"Erro de conexão com a API ({BASE_URL}): {exc}")

elif page == "👤 Meus Coroinhas":
    st.header("Meus Coroinhas")
    st.info("Em breve: lista personalizada de coroinhas por paróquia + status de disponibilidade.")

elif page == "📊 Dashboard":
    st.header("Dashboard Rápido")
    start_date, end_date = get_period()
    col1, col2, col3 = st.columns(3)

    try:
        escalas = get_json(
            "/api/escalas",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        col1.metric("Escalas Publicadas", sum(escala.get("published") is True for escala in escalas))
    except requests.RequestException:
        col1.metric("Escalas Publicadas", " indisponível")

    try:
        missas = get_json(
            "/api/missas",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        col2.metric("Missas Ativas", len(missas))
    except requests.RequestException:
        col2.metric("Missas Ativas", "indisponível")

    try:
        pessoas = get_json("/api/pessoas")
        col3.metric("Pessoas Cadastradas", len(pessoas))
    except requests.RequestException:
        col3.metric("Pessoas Cadastradas", "indisponível")

    st.caption("Dados atualizados ao recarregar a página.")

st.divider()
st.caption("Desenvolvido para a Paróquia São João Bosco | Versão MVP")
