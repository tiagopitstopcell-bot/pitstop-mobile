import streamlit as st
import sqlite3

# Configuração da página
st.set_page_config(page_title="PitStopCell", page_icon="📱", layout="wide")

# Função para conectar ao banco de dados SQLite
def get_connection():
    conn = sqlite3.connect('pitstop.db')
    return conn

# Garantir que as tabelas existam
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            cpf TEXT,
            email TEXT
        )
    """)
    
    # Tabela de Ordens de Serviço (OS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            aparelho TEXT NOT NULL,
            defeito TEXT NOT NULL,
            status TEXT NOT NULL,
            valor REAL,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
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
    
    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status != 'Concluída'")
    os_abertas = cursor.fetchone()[0]
    conn.close()

    col1.metric("Vendas Hoje", "R$ 0,00")
    col2.metric("Clientes Cadastrados", total_clientes)
    col3.metric("OS em Aberto", os_abertas)

# MÓDULO CRM / CLIENTES
elif modulo == "CRM / Clientes":
    st.header("👥 Gestão de Clientes")
    
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

# MÓDULO ORDEM DE SERVIÇO (OS)
elif modulo == "Ordem de Serviço (OS)":
    st.header("🛠️ Ordens de Serviço")
    
    aba1, aba2 = st.tabs(["➕ Nova OS", "📋 Gerenciar OS"])
    
    # Buscar lista de clientes para o seletor
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
    lista_clientes = cursor.fetchall()
    conn.close()
    
    dict_clientes = {f"{c[1]} (ID: {c[0]})": c[0] for c in lista_clientes}

    with aba1:
        st.subheader("Dar Entrada em OS")
        
        if not dict_clientes:
            st.warning("Cadastre pelo menos um cliente no módulo 'CRM / Clientes' antes de abrir uma OS.")
        else:
            with st.form("form_os", clear_on_submit=True):
                cliente_selecionado = st.selectbox("Selecione o Cliente *", options=list(dict_clientes.keys()))
                aparelho = st.text_input("Modelo do Aparelho (ex: iPhone 11, Moto G8) *")
                defeito = st.text_area("Defeito Relatado / Serviço a Realizar *")
                status = st.selectbox("Status Inicial", ["Em Análise", "Aguardando Peça", "Em Manutenção", "Pronto", "Concluída", "Cancelada"])
                valor = st.number_input("Orçamento Estimado (R$)", min_value=0.0, format="%.2f")
                observacoes = st.text_area("Observações Internas / Acessórios Deixados")
                
                submeter_os = st.form_submit_button("Salvar Ordem de Serviço")
                
                if submeter_os:
                    if not aparelho.strip() or not defeito.strip():
                        st.error("Preencha o modelo do aparelho e o defeito relatado!")
                    else:
                        cliente_id = dict_clientes[cliente_selecionado]
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO ordens_servico (cliente_id, aparelho, defeito, status, valor, observacoes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (cliente_id, aparelho, defeito, status, valor, observacoes))
                        conn.commit()
                        conn.close()
                        st.success(f"OS para **{aparelho}** criada com sucesso!")

    with aba2:
        st.subheader("Ordens de Serviço Cadastradas")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT os.id, c.nome, os.aparelho, os.defeito, os.status, os.valor, os.observacoes
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            ORDER BY os.id DESC
        """)
        dados_os = cursor.fetchall()
        conn.close()
        
        if dados_os:
            st.dataframe(
                dados_os,
                column_config={
                    "0": "Nº OS",
                    "1": "Cliente",
                    "2": "Aparelho",
                    "3": "Defeito",
                    "4": "Status",
                    "5": "Valor (R$)",
                    "6": "Obs"
                },
                use_container_width=True
            )
        else:
            st.info("Nenhuma Ordem de Serviço cadastrada ainda.")

# DEMAIS MÓDULOS
elif modulo == "Estoque":
    st.header("📦 Controle de Estoque")
    st.info("Módulo de Estoque pronto para uso.")

elif modulo == "PDV / Vendas":
    st.header("🛒 Ponto de Venda (PDV)")
    st.info("Módulo de Vendas pronto para uso.")

elif modulo == "Financeiro":
    st.header("💰 Controle Financeiro")
    st.info("Módulo Financeiro pronto para uso.")
