import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st
from database import init_db

NOME_LOGO = "Screenshot_20260924-093550.png"

# Configuração da página (Mobile First)
st.set_page_config(
    page_title="PitStop Cell — Sistema de OS",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()


def conectar_db():
    return sqlite3.connect("pitstop.db")


# --- NAVEGAÇÃO / SIDEBAR ---
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True)
    st.title("PitStop Cell")
    st.caption("Celulares e Informática")
    st.markdown("---")

    menu = st.radio(
        "Navegação",
        [
            "🏠 Painel OS",
            "🆕 Nova OS",
            "📦 Estoque & Peças",
            "👥 Clientes",
            "💰 Caixa & Relatórios",
        ],
    )
    st.markdown("---")
    st.caption(f"PitStop Cell © {date.today().year}")

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, width=90)
with col_titulo:
    st.title("PitStop Cell")
    st.caption("Gestão de Ordens de Serviço e Manutenção")

st.markdown("---")

# --- TELA 1: PAINEL DE OS ---
if menu == "🏠 Painel OS":
    st.subheader("📋 Ordens de Serviço")

    c1, c2 = st.columns([2, 1])
    with c1:
        busca = st.text_input("🔍 Buscar por OS, Cliente ou Aparelho")
    with c2:
        apenas_ativas = st.toggle("Apenas OS em Andamento", value=True)

    conn = conectar_db()
    cursor = conn.cursor()

    query = """
        SELECT o.id, o.data_entrada, c.nome, c.telefone, o.aparelho, o.defeito, o.status, o.total, o.garantia, o.imei
        FROM ordens o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE 1=1
    """
    params = []

    if busca:
        query += (
            " AND (c.nome LIKE ? OR o.aparelho LIKE ? OR CAST(o.id AS TEXT) = ?)"
        )
        params.extend([f"%{busca}%", f"%{busca}%", busca])

    if apenas_ativas:
        query += " AND o.status NOT IN ('Concluído', 'Cancelado', 'Entregue')"

    query += " ORDER BY o.id DESC"
    cursor.execute(query, params)
    ordens = cursor.fetchall()
    conn.close()

    if ordens:
        for (
            os_id,
            dt,
            cliente,
            tel,
            aparelho,
            defeito,
            status,
            total,
            garantia,
            imei,
        ) in ordens:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color: #1a1a1a; padding: 14px; border-radius: 8px; border-left: 6px solid #e50914; margin-bottom: 8px;">
                        <span style="font-size: 0.85rem; color: #e50914; font-weight: bold;">OS #{os_id} | Entrou em: {dt}</span><br>
                        <span style="font-size: 1.15rem; font-weight: bold; color: #ffffff;">👤 {cliente if cliente else 'Cliente s/ nome'}</span> 
                        <span style="font-size: 0.85rem; color: #aaaaaa;">({tel if tel else 'Sem Tel'})</span><br>
                        <span style="font-size: 0.95rem; color: #dddddd;">📱 <b>Aparelho:</b> {aparelho} {f'| IMEI: {imei}' if imei else ''}</span><br>
                        <span style="font-size: 0.9rem; color: #bbbbbb;">🛠️ <b>Defeito:</b> {defeito}</span><br>
                        <span style="font-size: 1.05rem; color: #28a745; font-weight: bold;">💰 Total: R$ {total:.2f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_st, col_pr = st.columns([1, 1])
                with col_st:
                    st.info(f"Status: {status}")
                with col_pr:
                    if st.button(f"📄 Imprimir Comprovante #{os_id}", key=f"p_{os_id}"):
                        st.subheader(f"🖨️ Comprovante PitStop Cell — OS #{os_id}")
                        st.text(f"""
==================================================
              PITSTOP CELL
        Celulares e Informática
==================================================
OS Nº: {os_id}          Data: {dt}
Cliente: {cliente}
Contato: {tel}
Aparelho: {aparelho}
Defeito: {defeito}
--------------------------------------------------
TOTAL: R$ {total:.2f}
Garantia: {garantia if garantia else '90 dias contra defeitos do serviço'}
Status Atual: {status}
==================================================
""")
                st.divider()
    else:
        st.info("Nenhuma Ordem de Serviço encontrada.")

# --- TELA 2: NOVA OS ---
elif menu == "🆕 Nova OS":
    st.subheader("➕ Nova Ordem de Serviço — PitStop Cell")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    lista_cli = cursor.fetchall()
    dict_cli = {nome: cid for cid, nome in lista_cli}

    cursor.execute(
        "SELECT id, descricao, preco_venda FROM produtos ORDER BY descricao"
    )
    lista_prod = cursor.fetchall()
    dict_prod = {f"{desc} (R$ {prec:.2f})": (pid, prec) for pid, desc, prec in lista_prod}
    conn.close()

    with st.form("form_os", clear_on_submit=True):
        st.markdown("### 1. Dados do Cliente")
        opt_cli = st.selectbox(
            "Cliente Cadastrado",
            ["-- Cadastrar Novo --"] + list(dict_cli.keys()),
        )

        c_nome = st.text_input("Nome do Novo Cliente")
        c_tel = st.text_input("Telefone / WhatsApp")

        st.markdown("### 2. Equipamento")
        col_a, col_b = st.columns(2)
        with col_a:
            aparelho = st.text_input(
                "Modelo do Aparelho", placeholder="Ex: Samsung A12"
            )
        with col_b:
            imei = st.text_input("IMEI / Nº de Série (Opcional)")

        defeito = st.text_area("Defeito Relatado pelo Cliente")
        diagnostico = st.text_area("Diagnóstico Técnico / Observações")

        st.markdown("### 3. Peça, Mão de Obra e Valores")
        opt_peca = st.selectbox(
            "Peça/Produto do Estoque",
            ["-- Nenhuma / Peça Própria --"] + list(dict_prod.keys()),
        )

        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            valor_peca = st.number_input(
                "Valor Peça (R$)", min_value=0.0, step=5.0
            )
        with col_v2:
            mao_obra = st.number_input(
                "Mão de Obra (R$)", min_value=0.0, step=10.0
            )
        with col_v3:
            desconto = st.number_input(
                "Desconto (R$)", min_value=0.0, step=5.0
            )

        garantia = st.text_input("Garantia", value="90 dias")
        status_in = st.selectbox(
            "Status Inicial",
            [
                "Recebido",
                "Em Análise",
                "Aguardando Peça",
                "Em Andamento",
                "Pronto",
            ],
        )

        salvar = st.form_submit_button("💾 Salvar OS na PitStop Cell", type="primary")

        if salvar:
            conn = conectar_db()
            cursor = conn.cursor()

            # Processa Cliente
            if opt_cli == "-- Cadastrar Novo --":
                if c_nome:
                    cursor.execute(
                        "INSERT INTO clientes (nome, telefone) VALUES (?, ?)",
                        (c_nome, c_tel),
                    )
                    cliente_id = cursor.lastrowid
                else:
                    cliente_id = None
            else:
                cliente_id = dict_cli[opt_cli]

            # Processa Peça
            peca_id = None
            if opt_peca != "-- Nenhuma / Peça Própria --":
                peca_id = dict_prod[opt_peca][0]

            total_calculado = (valor_peca + mao_obra) - desconto
            data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

            if aparelho and defeito:
                cursor.execute(
                    """
                    INSERT INTO ordens (data_entrada, cliente_id, aparelho, imei, defeito, diagnostico, peca_id, valor_peca, mao_de_obra, desconto, total, status, garantia)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data_hoje,
                        cliente_id,
                        aparelho,
                        imei,
                        defeito,
                        diagnostico,
                        peca_id,
                        valor_peca,
                        mao_obra,
                        desconto,
                        total_calculado,
                        status_in,
                        garantia,
                    ),
                )
                conn.commit()
                st.success(" Ordem de Serviço cadastrada com sucesso!")
            else:
                st.error("Preencha ao menos o modelo do aparelho e o defeito.")

            conn.close()

# --- TELA 3: ESTOQUE ---
elif menu == "📦 Estoque & Peças":
    st.subheader("📦 Controle de Estoque PitStop Cell")

    with st.expander("➕ Cadastrar Novo Item/Peça no Estoque"):
        with st.form("form_prod", clear_on_submit=True):
            p_cod = st.text_input("Código do Produto")
            p_desc = st.text_input("Descrição do Produto / Peça")
            p_cat = st.text_input("Categoria (ex: Tela, Bateria, Cabo)")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                p_qtd = st.number_input("Quantidade", min_value=0, step=1)
            with col_p2:
                p_cost = st.number_input("Custo (R$)", min_value=0.0, step=5.0)
            with col_p3:
                p_prec = st.number_input("Preço Venda (R$)", min_value=0.0, step=5.0)

            btn_prod = st.form_submit_button("Cadastrar Produto")

            if btn_prod and p_desc:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO produtos (codigo, descricao, categoria, quantidade, custo, preco_venda) VALUES (?, ?, ?, ?, ?, ?)",
                    (p_cod, p_desc, p_cat, p_qtd, p_cost, p_prec),
                )
                conn.commit()
                conn.close()
                st.success("Produto adicionado ao estoque!")

    conn = conectar_db()
    df_prod = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()

    if not df_prod.empty:
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado no estoque.")

# --- TELA 4: CLIENTES ---
elif menu == "👥 Clientes":
    st.subheader("👥 Clientes Cadastrados")
    conn = conectar_db()
    df_cli = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df_cli.empty:
        st.dataframe(df_cli, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado.")

# --- TELA 5: CAIXA ---
elif menu == "💰 Caixa & Relatórios":
    st.subheader("💰 Resumo Financeiro PitStop Cell")
    conn = conectar_db()
    df_os = pd.read_sql_query(
        "SELECT id, data_entrada, aparelho, total, status FROM ordens", conn
    )
    conn.close()

    if not df_os.empty:
        faturamento_total = df_os["total"].sum()
        st.metric("Faturamento Total Acumulado (OS)", f"R$ {faturamento_total:.2f}")
        st.dataframe(df_os, use_container_width=True)
    else:
        st.info("Nenhum lançamento financeiro registrado.")
