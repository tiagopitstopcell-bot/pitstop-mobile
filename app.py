import streamlit as st
import sqlite3

st.set_page_config(page_title="PitStopCell", page_icon="📱", layout="wide")

st.title("📱 PitStopCell - Gestão de Assistência")
st.success("Sistema rodando com sucesso no Streamlit Cloud!")

st.sidebar.title("Navegação")
modulo = st.sidebar.radio("Ir para:", ["Dashboard", "CRM / Clientes", "Estoque", "Ordem de Serviço (OS)", "PDV / Vendas", "Financeiro"])

if modulo == "Dashboard":
    st.header("📊 Dashboard Geral")
    col1, col2, col3 = st.columns(3)
    col1.metric("Vendas Hoje", "R$ 0,00")
    col2.metric("OS Abertas", "0")
    col3.metric("Estoque Baixo", "0 itens")

elif modulo == "CRM / Clientes":
    st.header("👥 Gestão de Clientes")
    st.info("Módulo de Clientes pronto para cadastro.")

elif modulo == "Estoque":
    st.header("📦 Controle de Estoque")
    st.info("Módulo de Estoque pronto para uso.")

elif modulo == "Ordem de Serviço (OS)":
    st.header("🛠️ Ordens de Serviço")
    st.info("Módulo de OS pronto para uso.")

elif modulo == "PDV / Vendas":
    st.header("🛒 Ponto de Venda (PDV)")
    st.info("Módulo de Vendas pronto para uso.")

elif modulo == "Financeiro":
    st.header("💰 Controle Financeiro")
    st.info("Módulo Financeiro pronto para uso.")
