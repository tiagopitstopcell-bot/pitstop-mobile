import os
import sqlite3
from datetime import date

import pandas as pd
import streamlit as st
from database import init_db

# Nome do arquivo da logo como salvo no GitHub
NOME_LOGO = "Screenshot_20260924-093550.png"

# 1. Configuração de Página (Mobile First)
st.set_page_config(
    page_title="PitStop Celulares e Informática",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inicializa o banco de dados
init_db()


# 2. Funções do Banco de Dados
def conectar_db():
    return sqlite3.connect("pitstop.db")


def cadastrar_cliente(nome, telefone):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def obter_clientes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    conn.close()
    return {nome: cid for cid, nome in clientes}


def cadastrar_os(cliente_id, aparelho, defeito, valor):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ordens (cliente_id, aparelho, defeito, valor, status) 
        VALUES (?, ?, ?, ?, ?)
    """,
        (cliente_id, aparelho, defeito, valor, "Em andamento"),
    )
    conn.commit()
    conn.close()


def obter_todas_os(termo="", somente_andamento=False):
    conn = conectar_db()
    cursor = conn.cursor()

    query = """
        SELECT o.id, c.nome, o.aparelho, o.defeito, o.status, o.valor
        FROM ordens o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE 1=1
    """
    params = []
    if termo:
        query += " AND (c.nome LIKE ? OR o.aparelho LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if somente_andamento:
        query += " AND o.status = 'Em andamento'"

    query += " ORDER BY o.id DESC"
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    return resultados


# 3. Sidebar com Logo da PitStop
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True)
    else:
        st.title("📱 PitStop")

    st.markdown("---")
    menu = st.radio(
        "Navegação",
        [
            "🏠 Painel Principal",
            "🆕 Nova OS",
            "👥 Clientes",
            "📊 Relatórios",
        ],
    )
    st.markdown("---")
    st.caption(f"PitStop Celulares e Informática © {date.today().year}")


# 4. Cabeçalho Principal da Tela
col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, width=100)
with col_titulo:
    st.title("PitStop OS Pro")
    st.caption("Sistema de Ordem de Serviço")

st.markdown("---")


# 5. Telas do Sistema
if menu == "🏠 Painel Principal":
    st.subheader("🏠 Painel de Ordens de Serviço")

    col1, col2 = st.columns([2, 1])
    with col1:
        busca = st.text_input("🔍 Buscar OS ou Cliente", placeholder="Pesquisar...")
    with col2:
        somente_andamento = st.toggle("Apenas Ativas", value=True)

    ordens = obter_todas_os(busca, somente_andamento)

    if ordens:
        for (
            os_id,
            cliente,
            aparelho,
            defeito,
            status,
            valor,
        ) in ordens:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 8px; border-left: 5px solid #d92525; margin-bottom: 10px;">
                        <span style="font-size: 0.85rem; color: #e15b5b; font-weight: bold;">OS #{os_id}</span><br>
                        <span style="font-size: 1.1rem; font-weight: bold; color: #ffffff;">{cliente if cliente else 'Cliente sem cadastro'}</span><br>
                        <span style="font-size: 0.95rem; color: #cccccc;">📱 <b>Aparelho:</b> {aparelho}</span><br>
                        <span style="font-size: 0.9rem; color: #aaaaaa;">📝 <b>Defeito:</b> {defeito}</span><br>
                        <span style="font-size: 1rem; color: #28a745; font-weight: bold;">💰 R$ {valor:.2f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_status, col_btn = st.columns([1, 1])
                with col_status:
                    if status == "Em andamento":
                        st.warning(f"Status: {status}")
                    else:
                        st.success(f"Status: {status}")
                with col_btn:
                    if st.button(f"🖨️ Imprimir #{os_id}", key=f"print_{os_id}"):
                        st.toast(
                            f"Gerando comprovante PitStop OS #{os_id}...",
                            icon="📄",
                        )

                st.divider()
    else:
        st.info("Nenhuma OS encontrada.")

elif menu == "🆕 Nova OS":
    st.subheader("🆕 Cadastrar Nova Ordem de Serviço")

    with st.form("form_nova_os", clear_on_submit=True):
        dict_clientes = obter_clientes()
        cliente_nome = st.selectbox(
            "Selecione o Cliente",
            options=["-- Novo Cliente --"] + list(dict_clientes.keys()),
        )

        novo_cliente_nome = st.text_input("Nome do Novo Cliente (se aplicável)")
        novo_cliente_tel = st.text_input("Telefone / WhatsApp")

        st.markdown("---")
        aparelho = st.text_input(
            "Modelo do Aparelho / Equipamento", placeholder="Ex: iPhone 11 / Notebook Dell"
        )
        defeito = st.text_area(
            "Defeito Relatado / Serviço a Realizar",
            placeholder="Descreva o problema ou solicitação",
        )
        valor = st.number_input("Valor Estimado (R$)", min_value=0.0, step=10.0)

        submit = st.form_submit_button("Criar Ordem de Serviço", type="primary")

        if submit:
            final_cliente_id = None
            if cliente_nome == "-- Novo Cliente --":
                if novo_cliente_nome:
                    final_cliente_id = cadastrar_cliente(
                        novo_cliente_nome, novo_cliente_tel
                    )
                else:
                    st.error("Informe o nome do novo cliente.")
            else:
                final_cliente_id = dict_clientes[cliente_nome]

            if final_cliente_id and aparelho and defeito:
                cadastrar_os(final_cliente_id, aparelho, defeito, valor)
                st.success(
                    "OS cadastrada com sucesso na PitStop Cell!", icon="✅"
                )
            else:
                st.warning("Preencha todos os campos obrigatórios.")

elif menu == "👥 Clientes":
    st.subheader("👥 Gestão de Clientes PitStop")
    st.info("Em breve: Cadastro completo e histórico de atendimentos.")

elif menu == "📊 Relatórios":
    st.subheader("📊 Faturamento e Relatórios")
    st.info("Em breve: Resumo financeiro de vendas e consertos.")
