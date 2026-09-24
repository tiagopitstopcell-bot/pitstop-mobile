import streamlit as st
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="PitStopCell", page_icon="📱", layout="wide")

# Função para conectar ao banco de dados SQLite
def get_connection():
    conn = sqlite3.connect('pitstop.db')
    return conn

# Garantir que todas as tabelas existam
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabela de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            cpf TEXT,
            email TEXT
        )
    """)
    
    # 2. Tabela de Ordens de Serviço (OS)
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

    # 3. Tabela de Estoque / Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_custo REAL,
            preco_venda REAL
        )
    """)

    # 4. Tabela de Vendas (PDV e Financeiro)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL
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

# ---------------------------------------------------------
# MÓDULO 1: DASHBOARD
# ---------------------------------------------------------
if modulo == "Dashboard":
    st.header("📊 Dashboard Geral")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status != 'Concluída' AND status != 'Cancelada'")
    os_abertas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM estoque WHERE quantidade <= 3")
    estoque_baixo = cursor.fetchone()[0]

    hoje = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(valor) FROM vendas WHERE data LIKE ?", (f"{hoje}%",))
    vendas_hoje = cursor.fetchone()[0] or 0.0
    
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vendas Hoje", f"R$ {vendas_hoje:.2f}")
    col2.metric("Clientes Cadastrados", total_clientes)
    col3.metric("OS em Aberto", os_abertas)
    col4.metric("Estoque Baixo (≤3)", estoque_baixo)

# ---------------------------------------------------------
# MÓDULO 2: CRM / CLIENTES
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# MÓDULO 3: ESTOQUE
# ---------------------------------------------------------
elif modulo == "Estoque":
    st.header("📦 Controle de Estoque e Peças")
    
    aba1, aba2 = st.tabs(["➕ Cadastrar Item", "📋 Consultar Estoque"])
    
    with aba1:
        st.subheader("Adicionar Peça / Produto")
        with st.form("form_estoque", clear_on_submit=True):
            nome_item = st.text_input("Nome do Produto/Peça *")
            qtd = st.number_input("Quantidade em Estoque *", min_value=1, step=1)
            preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
            preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f")
            
            submeter_item = st.form_submit_button("Salvar no Estoque")
            
            if submeter_item:
                if not nome_item.strip():
                    st.error("Informe o nome do item!")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO estoque (nome, quantidade, preco_custo, preco_venda) VALUES (?, ?, ?, ?)",
                        (nome_item, qtd, preco_custo, preco_venda)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Item **{nome_item}** adicionado ao estoque!")

    with aba2:
        st.subheader("Itens Cadastrados")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, quantidade, preco_custo, preco_venda FROM estoque ORDER BY id DESC")
        itens = cursor.fetchall()
        conn.close()
        
        if itens:
            st.dataframe(
                itens,
                column_config={
                    "0": "ID",
                    "1": "Produto / Peça",
                    "2": "Qtd",
                    "3": "Custo (R$)",
                    "4": "Venda (R$)"
                },
                use_container_width=True
            )
        else:
            st.info("Nenhum item cadastrado no estoque.")

# ---------------------------------------------------------
# MÓDULO 4: ORDEM DE SERVIÇO (OS)
# ---------------------------------------------------------
elif modulo == "Ordem de Serviço (OS)":
    st.header("🛠️ Ordens de Serviço")
    
    aba1, aba2 = st.tabs(["➕ Nova OS", "📋 Gerenciar OS"])
    
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
                aparelho = st.text_input("Modelo do Aparelho *")
                defeito = st.text_area("Defeito Relatado / Serviço *")
                status = st.selectbox("Status Inicial", ["Em Análise", "Aguardando Peça", "Em Manutenção", "Pronto", "Concluída", "Cancelada"])
                valor = st.number_input("Orçamento Estimado (R$)", min_value=0.0, format="%.2f")
                observacoes = st.text_area("Observações Internas")
                
                submeter_os = st.form_submit_button("Salvar Ordem de Serviço")
                
                if submeter_os:
                    if not aparelho.strip() or not defeito.strip():
                        st.error("Preencha o modelo do aparelho e o defeito!")
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

# ---------------------------------------------------------
# MÓDULO 5: PDV / VENDAS
# ---------------------------------------------------------
elif modulo == "PDV / Vendas":
    st.header("🛒 Ponto de Venda (PDV)")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, quantidade, preco_venda FROM estoque WHERE quantidade > 0")
    produtos = cursor.fetchall()
    conn.close()
    
    dict_produtos = {f"{p[1]} (Disp: {p[2]} | R$ {p[3]:.2f})": p for p in produtos}
    
    if not dict_produtos:
        st.warning("Nenhum produto com estoque disponível. Cadastre itens no módulo 'Estoque'.")
    else:
        with st.form("form_venda", clear_on_submit=True):
            prod_selecionado = st.selectbox("Selecione o Produto *", options=list(dict_produtos.keys()))
            qtd_venda = st.number_input("Quantidade *", min_value=1, step=1)
            
            concluir_venda = st.form_submit_button("Registrar Venda")
            
            if concluir_venda:
                item_dados = dict_produtos[prod_selecionado]
                item_id, item_nome, item_qtd, item_preco = item_dados[0], item_dados[1], item_dados[2], item_dados[3]
                
                if qtd_venda > item_qtd:
                    st.error(f"Quantidade insuficiente em estoque! Disponível: {item_qtd}")
                else:
                    valor_total = item_preco * qtd_venda
                    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    # Baixa no estoque
                    cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE id = ?", (qtd_venda, item_id))
                    # Lançamento no financeiro/vendas
                    cursor.execute(
                        "INSERT INTO vendas (descricao, valor, data, tipo) VALUES (?, ?, ?, ?)",
                        (f"Venda: {qtd_venda}x {item_nome}", valor_total, data_hoje, "PDV")
                    )
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Venda de {qtd_venda}x {item_nome} no valor de **R$ {valor_total:.2f}** realizada com sucesso!")

# ---------------------------------------------------------
# MÓDULO 6: FINANCEIRO
# ---------------------------------------------------------
elif modulo == "Financeiro":
    st.header("💰 Controle Financeiro")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM vendas")
    total_faturado = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT id, descricao, valor, data, tipo FROM vendas ORDER BY id DESC")
    historico = cursor.fetchall()
    conn.close()
    
    st.metric("Faturamento Total Registrado", f"R$ {total_faturado:.2f}")
    st.subheader("Histórico de Entradas")
    
    if historico:
        st.dataframe(
            historico,
            column_config={
                "0": "ID",
                "1": "Descrição",
                "2": "Valor (R$)",
                "3": "Data/Hora",
                "4": "Origem"
            },
            use_container_width=True
        )
    else:
        st.info("Nenhum lançamento financeiro até o momento.")
