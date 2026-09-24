import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st
from database import init_db

NOME_LOGO = "Screenshot_20260924-093550.png"

# Configuração da página (Mobile First)
st.set_page_config(
    page_title="PitStop Cell — Ordem de Serviço",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()


def conectar_db():
    return sqlite3.connect("pitstop.db")


# Controle de Estado da Navegação (Para os Botões do Painel funcionarem)
if "pagina" not in st.session_state:
    st.session_state.pagina = "🏠 Painel Principal"


def navegar_para(nome_pagina):
    st.session_state.pagina = nome_pagina


# --- SIDEBAR (Navegação Alternativa) ---
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True)
    st.title("PitStop Cell")
    st.caption("Celulares e Informática")
    st.markdown("---")

    opcoes_menu = [
        "🏠 Painel Principal",
        "🆕 Nova OS",
        "📦 Estoque & Peças",
        "👥 Clientes",
        "💰 Caixa & Financeiro",
    ]

    escolha = st.radio(
        "Navegação",
        opcoes_menu,
        index=opcoes_menu.index(st.session_state.pagina),
    )
    if escolha != st.session_state.pagina:
        st.session_state.pagina = escolha

    st.markdown("---")
    st.caption(f"PitStop Cell © {date.today().year}")

# --- CABEÇALHO DA LOJA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, width=80)
with col_tit:
    st.title("PitStop Cell")
    st.caption("Sistema de Ordem de Serviço Pró")

st.markdown("---")

# --- PAINEL DE BOTÕES DE ACESSO RÁPIDO (MENU VISUAL MOBILE) ---
st.write("### ⚡ Acesso Rápido")
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

with btn_col1:
    if st.button("🏠 Painel OS", use_container_width=True):
        navegar_para("🏠 Painel Principal")
        st.rerun()
with btn_col2:
    if st.button("🆕 Nova OS", use_container_width=True, type="primary"):
        navegar_para("🆕 Nova OS")
        st.rerun()
with btn_col3:
    if st.button("📦 Estoque", use_container_width=True):
        navegar_para("📦 Estoque & Peças")
        st.rerun()
with btn_col4:
    if st.button("👥 Clientes", use_container_width=True):
        navegar_para("👥 Clientes")
        st.rerun()
with btn_col5:
    if st.button("💰 Caixa", use_container_width=True):
        navegar_para("💰 Caixa & Financeiro")
        st.rerun()

st.markdown("---")


# ==========================================
# PÁGINA 1: PAINEL PRINCIPAL
# ==========================================
if st.session_state.pagina == "🏠 Painel Principal":
    st.subheader("🏠 Painel Geral & Ordens de Serviço")

    # Métricas / Resumo Rápido
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM ordens WHERE status NOT IN ('Concluído', 'Entregue', 'Cancelado')"
    )
    os_ativas = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM ordens")
    total_faturado = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(quantidade) FROM produtos")
    total_pecas = cursor.fetchone()[0] or 0
    conn.close()

    m1, m2, m3 = st.columns(3)
    m1.metric("OS em Andamento", f"{os_ativas}")
    m2.metric("Total em OS", f"R$ {total_faturado:.2f}")
    m3.metric("Peças no Estoque", f"{total_pecas} un.")

    st.markdown("---")

    # Busca e Filtros
    c1, c2 = st.columns([2, 1])
    with c1:
        busca = st.text_input(
            "🔍 Buscar por OS, Cliente ou Aparelho", placeholder="Ex: iPhone, João, #10..."
        )
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
        query += " AND (c.nome LIKE ? OR o.aparelho LIKE ? OR CAST(o.id AS TEXT) = ?)"
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
                        <span style="font-size: 0.85rem; color: #e50914; font-weight: bold;">OS #{os_id} | Entrou: {dt}</span><br>
                        <span style="font-size: 1.15rem; font-weight: bold; color: #ffffff;">👤 {cliente if cliente else 'Cliente s/ Cadastro'}</span> 
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
                    if st.button(
                        f"📄 Imprimir Comprovante #{os_id}", key=f"p_{os_id}"
                    ):
                        st.subheader(
                            f"🖨️ Comprovante PitStop Cell — OS #{os_id}"
                        )
                        st.code(
                            f"""
==================================================
              PITSTOP CELL
        Celulares e Informática
==================================================
OS Nº: {os_id}          Data: {dt}
Cliente: {cliente if cliente else 'Cliente Geral'}
Contato: {tel if tel else 'N/I'}
Aparelho: {aparelho}
Defeito: {defeito}
--------------------------------------------------
TOTAL: R$ {total:.2f}
Garantia: {garantia if garantia else '90 dias'}
Status: {status}
==================================================
""",
                            language="text",
                        )
                st.divider()
    else:
        st.info("Nenhuma Ordem de Serviço cadastrada ainda. Clique em '🆕 Nova OS' para começar!")


# ==========================================
# PÁGINA 2: NOVA OS
# ==========================================
elif st.session_state.pagina == "🆕 Nova OS":
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
    dict_prod = {
        f"{desc} (R$ {prec:.2f})": (pid, prec) for pid, desc, prec in lista_prod
    }
    conn.close()

    with st.form("form_os", clear_on_submit=True):
        st.markdown("### 1. Cliente")
        opt_cli = st.selectbox(
            "Cliente Cadastrado",
            ["-- Cadastrar Novo Cliente --"] + list(dict_cli.keys()),
        )
        c_nome = st.text_input("Nome do Novo Cliente (se aplicável)")
        c_tel = st.text_input("Telefone / WhatsApp")

        st.markdown("---")
        st.markdown("### 2. Equipamento")
        col_a, col_b = st.columns(2)
        with col_a:
            aparelho = st.text_input(
                "Modelo do Aparelho", placeholder="Ex: iPhone 11 / Moto G8"
            )
        with col_b:
            imei = st.text_input("IMEI / Nº de Série")

        defeito = st.text_area("Defeito Relatado")
        diagnostico = st.text_area("Diagnóstico Técnico / Observações")

        st.markdown("---")
        st.markdown("### 3. Peça, Mão de Obra e Valores")
        opt_peca = st.selectbox(
            "Selecione Peça do Estoque (opcional)",
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

        garantia = st.text_input("Termos de Garantia", value="90 dias contra defeitos do serviço")
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

            if opt_cli == "-- Cadastrar Novo Cliente --":
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
                st.success("✅ Ordem de Serviço cadastrada com sucesso!")
            else:
                st.error("Preencha ao menos o modelo do aparelho e o defeito.")

            conn.close()


# ==========================================
# PÁGINA 3: ESTOQUE
# ==========================================
elif st.session_state.pagina == "📦 Estoque & Peças":
    st.subheader("📦 Controle de Estoque PitStop Cell")

    with st.expander("➕ Cadastrar Novo Item/Peça no Estoque"):
        with st.form("form_prod", clear_on_submit=True):
            p_cod = st.text_input("Código do Produto")
            p_desc = st.text_input("Descrição (Ex: Tela Samsung A12)")
            p_cat = st.text_input("Categoria (Ex: Tela, Bateria, Cabo)")
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
                st.success("✅ Produto adicionado ao estoque!")

    conn = conectar_db()
    df_prod = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()

    if not df_prod.empty:
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado no estoque ainda.")


# ==========================================
# PÁGINA 4: CLIENTES
# ==========================================
elif st.session_state.pagina == "👥 Clientes":
    st.subheader("👥 Cadastro de Clientes")

    with st.expander("➕ Cadastrar Novo Cliente"):
        with st.form("form_cli_direto", clear_on_submit=True):
            n_nome = st.text_input("Nome Completo")
            n_tel = st.text_input("Telefone")
            n_whats = st.text_input("WhatsApp")
            n_cpf = st.text_input("CPF / CNPJ")
            btn_cli = st.form_submit_button("Salvar Cliente")

            if btn_cli and n_nome:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clientes (nome, telefone, whatsapp, cpf_cnpj) VALUES (?, ?, ?, ?)",
                    (n_nome, n_tel, n_whats, n_cpf),
                )
                conn.commit()
                conn.close()
                st.success("✅ Cliente cadastrado com sucesso!")

    conn = conectar_db()
    df_cli = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df_cli.empty:
        st.dataframe(df_cli, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")


# ==========================================
# PÁGINA 5: CAIXA
# ==========================================
elif st.session_state.pagina == "💰 Caixa & Financeiro":
    st.subheader("💰 Lançamentos de Caixa e Relatório")

    conn = conectar_db()
    df_os = pd.read_sql_query(
        "SELECT id AS 'OS Nº', data_entrada AS 'Data', aparelho AS 'Aparelho', total AS 'Valor Total (R$)', status AS 'Status' FROM ordens",
        conn,
    )
    conn.close()

    if not df_os.empty:
        faturamento_total = df_os["Valor Total (R$)"].sum()
        st.metric("Faturamento Acumulado (OS)", f"R$ {faturamento_total:.2f}")
        st.dataframe(df_os, use_container_width=True)
    else:
        st.info("Nenhum lançamento financeiro registrado até o momento.")
