import streamlit as st
import sqlite3

# Configuração da página
st.set_page_config(page_title="PitStopCell", page_icon="📱", layout="wide")

# Função para conectar ao banco de dados SQLite
def get_connection():
    conn = sqlite3.connect('pitstop.db')
    return conn

# Garantir que a tabela de clientes exista
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            cpf TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Título do App
st.title("📱 PitStopCell - Gestão de Assistência")

# Menu de Navegação Lateral
st.sidebar.title("Navegação")
modulo = st.sidebar.radio("Ir para:", ["Dashboard", "CRM / Clientes", "Estoque", "Ordem de Serviço (OS)", "PDV / Vendas", "Financeiro"])

# MÓDULO DASHBOARD
if modulo == "Dashboard":
    st.header("📊 Dashboard Geral")
    col1, col2, col3 = st.columns(3)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]
    conn.close()

    col1.metric("Vendas Hoje", "R$ 0,00")
    col2.metric("Clientes Cadastrados", total_clientes)
    col3.metric("OS Abertas", "0")

# MÓDULO CRM / CLIENTES
elif modulo == "CRM / Clientes":
    st.header("👥 Gestão de Clientes")
    
    # Aba para Cadastrar ou Listar
    aba1, aba2 = st.tabs(["➕ Cadastrar Cliente", "📋 Lista de Clientes"])
    
    with aba1:
        st.subheader("Novo Cadastro")
        with st.form("form_cliente", clear_on_submit=True):
            nome = st.text_input("Nome Completo *")
            telefone = st.text_input("Telefone / WhatsApp")
            cpf = st.text_input("CPF")
            email = st.text_input("E-mail")
            
            submetido = st.form_submit_button("Salvar Cliente")
            
            if submetido:
                if not nome.strip():
                    st.error("O campo 'Nome Completo' é obrigatório!")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO clientes (nome, telefone, cpf, email) VALUES (?, ?, ?, ?)",
                        (nome, telefone, cpf, email)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Cliente **{nome}** cadastrado com sucesso!")

    with aba2:
        st.subheader("Clientes Cadastrados")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, telefone, cpf, email FROM clientes ORDER BY id DESC")
        dados = cursor.fetchall()
        conn.close()
        
        if dados:
            st.dataframe(
                dados, 
                column_config={"0": "ID", "1": "Nome", "2": "Telefone", "3": "CPF", "4": "E-mail"},
                use_container_width=True
            )
        else:
            st.info("Nenhum cliente cadastrado ainda.")

# DEMAIS MÓDULOS
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
