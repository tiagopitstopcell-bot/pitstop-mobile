import base64
import os
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st
from database import init_db

NOME_LOGO = "IMG-20260924-WA0001.jpg"

# Configuração da Página Mobile First
st.set_page_config(
    page_title="PitStop Cell",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_db()


def conectar_db():
    return sqlite3.connect("pitstop.db")


# Controle de Navegação
if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"

if "impressao_os" not in st.session_state:
    st.session_state.impressao_os = None

# Converte imagem para Base64
logo_base64 = ""
if os.path.exists(NOME_LOGO):
    with open(NOME_LOGO, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode()

# --- CSS COM CORREÇÃO DE LEITURA E CORES ---
st.markdown(
    f"""
    <style>
    /* Fundo geral da aplicação */
    .stApp {{
        background-color: #f4f6f9 !important;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}

    /* Forçar cor do texto para escuro em toda a tela */
    h1, h2, h3, h4, h5, h6, p, label, span, div {{
        color: #1f2937 !important;
    }}

    /* Barra Superior Azul */
    .top-header {{
        background-color: #2563eb;
        padding: 12px 15px;
        color: white !important;
        display: flex;
        align-items: center;
        gap: 12px;
        border-radius: 0 0 12px 12px;
        margin-top: -60px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 6px rgba(0,0,0,0.1);
    }}
    .top-header p, .top-header span {{
        color: white !important;
    }}
    .logo-circulo {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        background-color: white;
        border: 2px solid white;
    }}
    .header-title {{
        font-size: 18px;
        font-weight: bold;
        margin: 0;
    }}
    .header-subtitle {{
        font-size: 12px;
        margin: 0;
        opacity: 0.9;
    }}

    /* Botões da Tela Inicial */
    div.stButton > button {{
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 18px 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05) !important;
        width: 100% !important;
    }}
    div.stButton > button:hover {{
        border-color: #2563eb !important;
        color: #2563eb !important;
    }}

    /* Caixas de Texto / Form */
    div[data-baseweb="input"] > div {{
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
    }}
    input {{
        color: #1f2937 !important;
    }}

    /* Card de Itens */
    .card-item {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- CABEÇALHO AZUL PITSTOP CELL ---
tag_img = (
    f'<img src="data:image/jpeg;base64,{logo_base64}" class="logo-circulo">'
    if logo_base64
    else '<div class="logo-circulo" style="display:flex;align-items:center;justify-content:center;color:#2563eb;font-weight:bold;">PS</div>'
)

st.markdown(
    f"""
    <div class="top-header">
        {tag_img}
        <div>
            <p class="header-title">PitStop Cell</p>
            <p class="header-subtitle">Assistência Técnica e Celulares</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 🏠 TELA INICIAL
# ==========================================
if st.session_state.pagina == "Início":

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋\n\nOrdem Serviço", use_container_width=True):
            st.session_state.pagina = "OS_LISTA"
            st.rerun()

        if st.button("👥\n\nClientes", use_container_width=True):
            st.session_state.pagina = "CLIENTES"
            st.rerun()

        if st.button("🛒\n\nProdutos", use_container_width=True):
            st.session_state.pagina = "PRODUTOS"
            st.rerun()

    with col2:
        if st.button("🆕\n\nNova OS", use_container_width=True):
            st.session_state.pagina = "NOVA_OS"
            st.rerun()

        if st.button("💰\n\nFluxo de Caixa", use_container_width=True):
            st.session_state.pagina = "CAIXA"
            st.rerun()

        if st.button("📊\n\nRelatório Pedidos", use_container_width=True):
            st.session_state.pagina = "CAIXA"
            st.rerun()


# ==========================================
# 👥 CLIENTES (COM FORMULÁRIO ABERTO E VISÍVEL)
# ==========================================
elif st.session_state.pagina == "CLIENTES":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()

    st.subheader("👥 Cadastro e Gestão de Clientes")

    st.markdown("#### ➕ Cadastrar Novo Cliente")
    with st.form("form_cli_aberto", clear_on_submit=True):
        nome = st.text_input("Nome Completo do Cliente")
        tel = st.text_input("Telefone / WhatsApp")
        cpf = st.text_input("CPF / CNPJ")
        btn_c = st.form_submit_button("💾 Salvar Cliente", type="primary")

        if btn_c:
            if nome:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clientes (nome, telefone, cpf_cnpj) VALUES (?, ?, ?)",
                    (nome, tel, cpf),
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Cliente '{nome}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, digite o nome do cliente.")

    st.markdown("---")
    st.markdown("#### 📜 Clientes Cadastrados")

    conn = conectar_db()
    df_cli = pd.read_sql_query("SELECT id AS 'ID', nome AS 'Nome', telefone AS 'Telefone', cpf_cnpj AS 'CPF/CNPJ' FROM clientes ORDER BY nome", conn)
    conn.close()

    if not df_cli.empty:
        st.dataframe(df_cli, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")


# ==========================================
# 📋 ORDENS DE SERVIÇO
# ==========================================
elif st.session_state.pagina == "OS_LISTA":
    col_back, col_new = st.columns([2, 1])
    with col_back:
        if st.button("← Voltar ao Início"):
            st.session_state.pagina = "Início"
            st.rerun()
    with col_new:
        if st.button("➕ Nova OS"):
            st.session_state.pagina = "NOVA_OS"
            st.rerun()

    st.subheader("📋 Ordens de Serviço")

    busca = st.text_input("🔍 Buscar por OS ou Cliente")
    somente_andamento = st.toggle("Apenas OS em andamento", value=True)

    conn = conectar_db()
    cursor = conn.cursor()

    query = """
        SELECT o.id, o.data_entrada, o.previsao_saida, c.nome, o.aparelho, o.status, o.total, o.defeito, o.cor, c.telefone
        FROM ordens o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE 1=1
    """
    params = []

    if busca:
        query += " AND (c.nome LIKE ? OR o.aparelho LIKE ? OR CAST(o.id AS TEXT) = ?)"
        params.extend([f"%{busca}%", f"%{busca}%", busca])

    if somente_andamento:
        query += " AND o.status NOT IN ('Pronto', 'Concluído', 'Entregue', 'Cancelado')"

    query += " ORDER BY o.id DESC"
    cursor.execute(query, params)
    ordens = cursor.fetchall()
    conn.close()

    if ordens:
        for (
            os_id,
            dt_in,
            dt_out,
            cliente,
            aparelho,
            status,
            total,
            defeito,
            cor,
            tel,
        ) in ordens:
            st.markdown(
                f"""
                <div class="card-item">
                    <div style="display:flex; justify-content:space-between;">
                        <b>OS Nº: #{os_id}</b>
                        <span style="background-color:#2563eb; color:white; padding:2px 8px; border-radius:10px; font-size:12px;">{status}</span>
                    </div>
                    <div style="font-size:13px; color:#374151; margin-top:5px;">
                        <b>Cliente:</b> {cliente if cliente else 'S/ Cadastro'} ({tel if tel else 'S/ Tel'})<br>
                        <b>Aparelho:</b> {aparelho} {f'({cor})' if cor else ''}<br>
                        <b>Defeito:</b> {defeito}<br>
                        <b>Total:</b> <span style="color:#16a34a; font-weight:bold;">R$ {total:.2f}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_act1, c_act2 = st.columns(2)
            with c_act1:
                if st.button(f"🖨️ Imprimir #{os_id}", key=f"pr_{os_id}"):
                    st.session_state.impressao_os = os_id
            with c_act2:
                if st.button(f"✅ Finalizar #{os_id}", key=f"fin_{os_id}"):
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE ordens SET status = 'Pronto' WHERE id = ?",
                        (os_id,),
                    )
                    conn.commit()
                    conn.close()
                    st.success("OS Finalizada!")
                    st.rerun()

            st.divider()

        # Modal de Impressão
        if st.session_state.impressao_os:
            os_sel = st.session_state.impressao_os
            st.markdown("---")
            st.subheader(f"🖨️ Comprovante — OS #{os_sel}")

            tipo_imp = st.radio(
                "Formato:",
                ["Impressão A4 (Completa)", "Térmica (Cupom)"],
                horizontal=True,
            )

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT o.id, o.data_entrada, o.previsao_saida, c.nome, c.cpf_cnpj, c.telefone,
                       o.marca, o.aparelho, o.cor, o.imei, o.acessorios, o.defeito,
                       o.valor_peca, o.mao_de_obra, o.desconto, o.total, o.garantia
                FROM ordens o LEFT JOIN clientes c ON o.cliente_id = c.id WHERE o.id = ?
            """,
                (os_sel,),
            )
            d = cursor.fetchone()
            conn.close()

            if d:
                if tipo_imp == "Impressão A4 (Completa)":
                    st.code(
                        f"""
================================================================
                    PITSTOP CELL - ORDENS DE SERVIÇO Nº {d[0]}
================================================================
CLIENTE: {d[3]} | FONE: {d[5]} | CPF: {d[4] if d[4] else 'N/I'}
EQUIPAMENTO: {d[6]} {d[7]} ({d[8]}) | IMEI: {d[9]}
ACESSÓRIOS: {d[10]}
DEFEITO: {d[11]}
----------------------------------------------------------------
SERVIÇOS: R$ {d[13]:.2f} | PEÇAS: R$ {d[12]:.2f} | DESC: R$ {d[14]:.2f}
TOTAL DA OS: R$ {d[15]:.2f}
GARANTIA: {d[16]}
================================================================
""",
                        language="text",
                    )
                else:
                    st.code(
                        f"""
========================================
              PITSTOP CELL
========================================
OS Nº: {d[0]}      Data: {d[1]}
CLIENTE: {d[3]}
APARELHO: {d[7]}
DEFEITO: {d[11]}
TOTAL: R$ {d[15]:.2f}
========================================
""",
                        language="text",
                    )

            if st.button("Fechar Comprovante"):
                st.session_state.impressao_os = None
                st.rerun()
    else:
        st.info("Nenhuma OS encontrada.")


# ==========================================
# 🆕 FORMULÁRIO DE NOVA OS
# ==========================================
elif st.session_state.pagina == "NOVA_OS":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()

    st.subheader("🆕 Cadastrar Nova OS")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    lista_cli = cursor.fetchall()
    dict_cli = {nome: cid for cid, nome in lista_cli}
    conn.close()

    with st.form("form_nova_os"):
        st.markdown("### 👤 Cliente")
        opt_cli = st.selectbox(
            "Cliente Cadastrado",
            ["-- Cadastrar Novo Cliente --"] + list(dict_cli.keys()),
        )
        c_nome = st.text_input("Nome do Novo Cliente")
        c_tel = st.text_input("Telefone / WhatsApp")

        st.markdown("---")
        st.markdown("### 📱 Equipamento")
        marca = st.text_input("Marca (Ex: Samsung, Apple, Motorola)")
        aparelho = st.text_input("Modelo do Aparelho (Ex: iPhone 11)")
        cor = st.text_input("Cor do Aparelho")
        imei = st.text_input("IMEI / Nº de Série")
        senha = st.text_input("Senha / Padrão de Desbloqueio")
        acessorios = st.text_input("Acessórios Deixados")
        defeito = st.text_area("Defeito Relatado")

        st.markdown("---")
        st.markdown("### 💰 Valores & Garantia")
        v_peca = st.number_input("Valor Peças (R$)", min_value=0.0, step=5.0)
        v_obra = st.number_input("Mão de Obra (R$)", min_value=0.0, step=10.0)
        v_desc = st.number_input("Desconto (R$)", min_value=0.0, step=5.0)
        garantia = st.text_input("Garantia", value="90 dias")
        cond_pag = st.selectbox(
            "Forma de Pagamento", ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"]
        )

        salvar = st.form_submit_button("💾 Salvar Ordem de Serviço", type="primary")

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

            total_calc = (v_peca + v_obra) - v_desc
            dt_hoje = datetime.now().strftime("%d/%m/%Y")

            if aparelho and defeito:
                cursor.execute(
                    """
                    INSERT INTO ordens (data_entrada, cliente_id, marca, aparelho, cor, imei, senha, acessorios, defeito, valor_peca, mao_de_obra, desconto, total, status, garantia, condicao_pagamento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        dt_hoje,
                        cliente_id,
                        marca,
                        aparelho,
                        cor,
                        imei,
                        senha,
                        acessorios,
                        defeito,
                        v_peca,
                        v_obra,
                        v_desc,
                        total_calc,
                        "Em orçamento",
                        garantia,
                        cond_pag,
                    ),
                )

                if total_calc > 0:
                    cursor.execute(
                        "INSERT INTO caixa (data, tipo, descricao, valor, forma_pagamento) VALUES (?, ?, ?, ?, ?)",
                        (
                            dt_hoje,
                            "Entrada",
                            f"OS #{aparelho} - {c_nome if c_nome else 'Cliente'}",
                            total_calc,
                            cond_pag,
                        ),
                    )

                conn.commit()
                st.success("✅ OS Cadastrada com Sucesso!")
                st.session_state.pagina = "OS_LISTA"
                st.rerun()
            else:
                st.error("Preencha ao menos o Modelo e o Defeito.")

            conn.close()


# ==========================================
# 🛒 PRODUTOS / ESTOQUE
# ==========================================
elif st.session_state.pagina == "PRODUTOS":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()

    st.subheader("🛒 Produtos & Peças em Estoque")

    st.markdown("#### ➕ Cadastrar Novo Produto")
    with st.form("form_prod_aberto", clear_on_submit=True):
        p_desc = st.text_input("Descrição do Produto / Peça")
        p_cat = st.text_input("Categoria (ex: Tela, Bateria, Cabo)")
        p_prec = st.number_input("Preço de Venda (R$)", min_value=0.0)
        p_qtd = st.number_input("Quantidade", min_value=1, value=1)
        btn_prod = st.form_submit_button("💾 Salvar Produto", type="primary")

        if btn_prod and p_desc:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO produtos (descricao, categoria, preco_venda, quantidade) VALUES (?, ?, ?, ?)",
                (p_desc, p_cat, p_prec, p_qtd),
            )
            conn.commit()
            conn.close()
            st.success("Produto Cadastrado!")
            st.rerun()

    st.markdown("---")
    conn = conectar_db()
    df_prod = pd.read_sql_query("SELECT id AS 'ID', descricao AS 'Descrição', categoria AS 'Categoria', preco_venda AS 'Preço (R$)', quantidade AS 'Qtd' FROM produtos", conn)
    conn.close()

    if not df_prod.empty:
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("Nenhum produto em estoque.")


# ==========================================
# 💰 FLUXO DE CAIXA
# ==========================================
elif st.session_state.pagina == "CAIXA":
    if st.button("← Voltar ao Início"):
        st.session_state.pagina = "Início"
        st.rerun()

    st.subheader("💰 Fluxo de Caixa")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM caixa WHERE tipo = 'Entrada'")
    ent = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(valor) FROM caixa WHERE tipo = 'Saída'")
    sai = cursor.fetchone()[0] or 0.0
    conn.close()

    st.metric("Saldo do Caixa", f"R$ {(ent - sai):.2f}")

    conn = conectar_db()
    df_cx = pd.read_sql_query(
        "SELECT id AS 'Nº', data AS 'Data', tipo AS 'Tipo', descricao AS 'Descrição', valor AS 'Valor (R$)', forma_pagamento AS 'Pagamento' FROM caixa ORDER BY id DESC",
        conn,
    )
    conn.close()

    if not df_cx.empty:
        st.dataframe(df_cx, use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada.")
