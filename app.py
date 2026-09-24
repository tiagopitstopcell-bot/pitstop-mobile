import os
import sqlite3
import streamlit as st
from database import init_db

NOME_LOGO = "IMG-20260924-WA0001.jpg"

# Configuração da Página
st.set_page_config(
    page_title="PitStop Cell",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_db()

if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"

# CSS PERSONALIZADO PARA COPIAR O LAYOUT DA IMAGEM
st.markdown(
    """
    <style>
    /* Fundo geral claro */
    .stApp {
        background-color: #f5f5f5 !important;
    }

    /* Esconde barra lateral e cabeçalho padrão */
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }

    /* Barra Superior Azul */
    .top-header {
        background-color: #3b82f6;
        padding: 15px;
        color: white;
        display: flex;
        align-items: center;
        gap: 15px;
        border-radius: 0 0 10px 10px;
        margin-top: -60px;
        margin-bottom: 20px;
    }
    .logo-circulo {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        background-color: white;
        border: 2px solid white;
    }
    .header-title {
        font-size: 20px;
        font-weight: bold;
        margin: 0;
        color: white;
    }
    .header-subtitle {
        font-size: 13px;
        margin: 0;
        opacity: 0.9;
        color: white;
    }

    /* Ajuste dos Botões em Grade */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #4b5563 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 25px 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0px 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        width: 100% !important;
        height: 100px !important;
    }

    div.stButton > button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CABEÇALHO AZUL (IGUAL À IMAGEM) ---
st.markdown(
    f"""
    <div class="top-header">
        <div>
            <p class="header-title">Bem-vindo</p>
            <p class="header-subtitle">PitStop Cell — Assistência Técnica</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- NAVEGAÇÃO ENTRE TELAS ---
if st.session_state.pagina == "Início":

    # GRADE DE BOTÕES (2 COLUNAS IGUAL À IMAGEM)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋\n\nOrdem Serviço", use_container_width=True):
            st.session_state.pagina = "OS"
            st.rerun()

        if st.button("👥\n\nClientes", use_container_width=True):
            st.session_state.pagina = "Clientes"
            st.rerun()

        if st.button("📄\n\nTipo", use_container_width=True):
            st.session_state.pagina = "OS"
            st.rerun()

        if st.button("💳\n\nCondição de Pagamento", use_container_width=True):
            st.session_state.pagina = "Caixa"
            st.rerun()

        if st.button("🛒\n\nProdutos", use_container_width=True):
            st.session_state.pagina = "Produtos"
            st.rerun()

    with g2 if "g2" in locals() else col2:
        if st.button("👤\n\nMeus Dados", use_container_width=True):
            st.session_state.pagina = "Clientes"
            st.rerun()

        if st.button("☁️\n\nImportar Clientes", use_container_width=True):
            st.session_state.pagina = "Clientes"
            st.rerun()

        if st.button("📜\n\nCondição de Garantia", use_container_width=True):
            st.session_state.pagina = "OS"
            st.rerun()

        if st.button("📚\n\nCategoria de Produto", use_container_width=True):
            st.session_state.pagina = "Produtos"
            st.rerun()

        if st.button("📊\n\nRelatório Pedidos", use_container_width=True):
            st.session_state.pagina = "Caixa"
            st.rerun()

elif st.session_state.pagina == "OS":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()
    st.title("📋 Ordens de Serviço")
    st.info("Lista de Ordens de Serviço")

elif st.session_state.pagina == "Produtos":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()
    st.title("🛒 Produtos & Estoque")
    st.info("Lista de Produtos")

elif st.session_state.pagina == "Clientes":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()
    st.title("👥 Clientes")
    st.info("Lista de Clientes")

elif st.session_state.pagina == "Caixa":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()
    st.title("💰 Caixa & Relatórios")
    st.info("Fluxo de Caixa")
