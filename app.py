import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st
from database import init_db

NOME_LOGO = "IMG-20260924-WA0001.jpg"

# Configuração Mobile Primeiro
st.set_page_config(
    page_title="PitStop Cell — Assistência Técnica",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()


def conectar_db():
    return sqlite3.connect("pitstop.db")


if "pagina" not in st.session_state:
    st.session_state.pagina = "📋 Ordens de Serviço"

if "impressao_os" not in st.session_state:
    st.session_state.impressao_os = None


def navegar_para(nome_pagina):
    st.session_state.pagina = nome_pagina


# ESTILO VISUAL DA PITSTOP CELL
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
    }
    .card-os {
        background-color: #1a1d24;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.2);
        border: 1px solid #2b303c;
        margin-bottom: 12px;
    }
    .badge-status {
        padding: 4px 12px;
        border-radius: 15px;
        color: white;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- NAVEGAÇÃO LATERAL (MENU HAMBÚRGUER) ---
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True)
    st.title("PitStop Cell")
    st.caption("Assistência Técnica e Celulares")
    st.markdown("---")
    menu = st.radio(
        "Navegar",
        [
            "📋 Ordens de Serviço",
            "🆕 Nova OS",
            "📦 Produtos",
            "👥 Clientes",
            "💰 Caixa & Relatórios",
        ],
        index=[
            "📋 Ordens de Serviço",
            "🆕 Nova OS",
            "📦 Produtos",
            "👥 Clientes",
            "💰 Caixa & Relatórios",
        ].index(
            st.session_state.pagina
            if st.session_state.pagina in ["📋 Ordens de Serviço", "🆕 Nova OS", "📦 Produtos", "👥 Clientes", "💰 Caixa & Relatórios"]
            else "📋 Ordens de Serviço"
        ),
    )
    if menu != st.session_state.pagina:
        st.session_state.pagina = menu


# --- BANNER COMPLETO DO TOPO ---
if os.path.exists(NOME_LOGO):
    st.image(NOME_LOGO, use_container_width=True)
else:
    st.markdown("<h2 style='text-align: center;'>PitStop Cell</h2>", unsafe_allow_html=True)

st.markdown("---")

# --- BOTÕES DE ACESSO RÁPIDO (A BARRINHA VERMELHA DESTACA A PÁGINA ATIVA) ---
st.caption("⚡ **Menu Principal**")

# Definir os botões e suas páginas associadas
b_os = "primary" if st.session_state.pagina == "📋 Ordens de Serviço" else "secondary"
b_nova = "primary" if st.session_state.pagina == "🆕 Nova OS" else "secondary"
b_prod = "primary" if st.session_state.pagina == "📦 Produtos" else "secondary"
b_cli = "primary" if st.session_state.pagina == "👥 Clientes" else "secondary"
b_cx = "primary" if st.session_state.pagina == "💰 Caixa & Relatórios" else "secondary"

if st.button("📋 Ordens de Serviço", use_container_width=True, type=b_os):
    navegar_para("📋 Ordens de Serviço")
    st.rerun()

if st.button("🆕 Nova OS", use_container_width=True, type=b_nova):
    navegar_para("🆕 Nova OS")
    st.rerun()

if st.button("📦 Produtos / Peças", use_container_width=True, type=b_prod):
    navegar_para("📦 Produtos")
    st.rerun()

if st.button("👥 Clientes", use_container_width=True, type=b_cli):
    navegar_para("👥 Clientes")
    st.rerun()

if st.button("💰 Fluxo de Caixa / Relatórios", use_container_width=True, type=b_cx):
    navegar_para("💰 Caixa & Relatórios")
    st.rerun()

st.markdown("---")


# ==========================================
# PAINEL DE ORDENS DE SERVIÇO
# ==========================================
if st.session_state.pagina == "📋 Ordens de Serviço":
    st.subheader("📋 Painel de OS")

    busca = st.text_input("🔍 OS ou Cliente", placeholder="Pesquisar...")
    somente_andamento = st.toggle("Listar somente OS em andamento", value=True)

    conn = conectar_db()
    cursor = conn.cursor()

    query = """
        SELECT o.id, o.data_entrada, o.previsao_saida, c.nome, o.aparelho, o.status, o.total, o.defeito, o.cor, o.senha, o.acessorios, c.telefone
        FROM ordens o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE 1=1
    """
    params = []

    if busca:
        query += " AND (c.nome LIKE ? OR o.aparelho LIKE ? OR CAST(o.id AS TEXT) = ?)"
        params.extend([f"%{busca}%", f"%{busca}%", busca])

    if somente_andamento:
        query += " AND o.status NOT IN ('Concluído', 'Entregue', 'Cancelado')"

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
            senha,
            acessorios,
            tel,
        ) in ordens:
            with st.container():
                cor_badge = "#007bff"
                if "Aguardando" in status:
                    cor_badge = "#dc3545"
                elif "Andamento" in status or "orçamento" in status:
                    cor_badge = "#ffc107"
                elif "Pronto" in status or "Concluído" in status:
                    cor_badge = "#28a745"

                st.markdown(
                    f"""
                    <div class="card-os">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#ffffff;">OS Nº: {os_id}</strong>
                            <span class="badge-status" style="background-color: {cor_badge};">{status}</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #cccccc; margin-top:8px;">
                            <b>Data Entrada:</b> {dt_in} | <b>Previsão:</b> {dt_out if dt_out else 'N/I'}<br>
                            <b>Cliente:</b> {cliente if cliente else 'Não Identificado'} ({tel if tel else ''})<br>
                            <b>Aparelho:</b> {aparelho} {f'({cor})' if cor else ''}<br>
                            <b>Defeito:</b> {defeito}<br>
                            <b>Total:</b> <span style="color:#28a745; font-weight:bold;">R$ {total:.2f}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                c_act1, c_act2, c_act3 = st.columns([1, 1, 1])
                with c_act1:
                    if st.button(f"🖨️ Imprimir", key=f"pr_{os_id}"):
                        st.session_state.impressao_os = os_id
                with c_act2:
                    if st.button(f"✏️ Editar", key=f"ed_{os_id}"):
                        st.toast(f"Edição para OS #{os_id} em breve.", icon="✏️")
                with c_act3:
                    if st.button(f"✅ Finalizar", key=f"fin_{os_id}"):
                        conn = conectar_db()
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE ordens SET status = 'Pronto' WHERE id = ?",
                            (os_id,),
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"OS #{os_id} Finalizada!")
                        st.rerun()

                st.divider()

        # MODAL / COMPROVANTE DE IMPRESSÃO
        if st.session_state.impressao_os:
            os_sel = st.session_state.impressao_os
            st.markdown("---")
            st.subheader(f"🖨️ Opções de Impressão — OS #{os_sel}")

            tipo_imp = st.radio(
                "Qual tipo de impressão deseja?",
                ["Impressão A4 (Completa)", "Térmica (Cupom)"],
                horizontal=True,
            )

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT o.id, o.data_entrada, o.previsao_saida, c.nome, c.cpf_cnpj, c.telefone, c.endereco,
                       o.marca, o.aparelho, o.cor, o.imei, o.acessorios, o.defeito, o.diagnostico,
                       o.valor_peca, o.mao_de_obra, o.desconto, o.total, o.garantia, o.condicao_pagamento
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
================================================================================
                                ORDEM DE SERVIÇO Nº {d[0]}
                                PitStop Cell
================================================================================
DADOS DO CLIENTE
Nome: {d[3]}
Endereço: {d[6] if d[6] else 'N/I'}
Telefone: {d[5]}                  CPF/CNPJ: {d[4] if d[4] else 'N/I'}
--------------------------------------------------------------------------------
INFORMAÇÕES DO PRODUTO
Marca: {d[7]}          Modelo: {d[8]}          Cor: {d[9]}
IMEI/Série: {d[10]}    Acessórios: {d[11]}
--------------------------------------------------------------------------------
DIAGNÓSTICO E SERVIÇO A SER PRESTADO
Reclamação/Defeito: {d[12]}
Solução/Diagnóstico: {d[13]}
--------------------------------------------------------------------------------
ORÇAMENTO & GARANTIA
Serviços: R$ {d[15]:.2f}    Peças: R$ {d[14]:.2f}    Desconto: R$ {d[16]:.2f}
VALOR FINAL: R$ {d[17]:.2f}
Garantia até: {d[18]} | Condição: {d[19] if d[19] else 'À Vista/Cartão'}
--------------------------------------------------------------------------------
CHECKLIST GERAL DE DIAGNÓSTICO
[X] Estado Geral   [X] Botões/Tela   [X] Conectividade   [X] Bateria/Carga
================================================================================
""",
                        language="text",
                    )
                else:
                    st.code(
                        f"""
========================================
              PITSTOP CELL
        Assistência Técnica
========================================
OS Nº: {d[0]}
Data Entrada: {d[1]}
Previsão Saída: {d[2]}
----------------------------------------
CLIENTE: {d[3]}
FONE: {d[5]}
----------------------------------------
EQUIPAMENTO: {d[8]} ({d[9]})
DEFEITO: {d[12]}
----------------------------------------
TOTAL: R$ {d[17]:.2f}
Garantia: {d[18]}
========================================
""",
                        language="text",
                    )

            if st.button("Fechar Impressão"):
                st.session_state.impressao_os = None
                st.rerun()
    else:
        st.info("Nenhuma Ordem de Serviço encontrada.")


# ==========================================
# FORMULÁRIO COMPLETO DE NOVA OS
# ==========================================
elif st.session_state.pagina == "🆕 Nova OS":
    st.subheader("🆕 Cadastrar Nova Ordem de Serviço")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    lista_cli = cursor.fetchall()
    dict_cli = {nome: cid for cid, nome in lista_cli}
    conn.close()

    with st.form("form_nova_os_pro", clear_on_submit=True):
        st.markdown("### 👤 Cliente")
        opt_cli = st.selectbox(
            "Cliente", ["-- Novo Cliente --"] + list(dict_cli.keys())
        )
        c_nome = st.text_input("Nome Completo")
        c_tel = st.text_input("Telefone / WhatsApp")

        st.markdown("---")
        st.markdown("### 📱 Equipamento")
        col1, col2 = st.columns(2)
        with col1:
            marca = st.text_input("Marca (Ex: Motorola, Apple, Samsung)")
            aparelho = st.text_input("Modelo (Ex: Moto G8, iPhone 11)")
            cor = st.text_input("Cor (Ex: Azul, Preto)")
        with col2:
            dt_saida = st.date_input("Previsão de Saída")
            imei = st.text_input("Número de Série / IMEI")
            senha = st.text_input("Senha / Padrão do Aparelho")

        acessorios = st.text_input(
            "Acessórios Deixados", placeholder="Ex: Deixou capa e carregador"
        )
        defeito = st.text_area("Defeito / Reclamação")

        st.markdown("---")
        st.markdown("### 💰 Orçamento & Serviços")
        c_v1, c_v2, c_v3 = st.columns(3)
        with c_v1:
            valor_peca = st.number_input(
                "Valor Peças (R$)", min_value=0.0, step=5.0
            )
        with c_v2:
            mao_obra = st.number_input(
                "Mão de Obra (R$)", min_value=0.0, step=10.0
            )
        with c_v3:
            desconto = st.number_input("Desconto (R$)", min_value=0.0, step=5.0)

        garantia = st.text_input("Garantia", value="30 dias")
        cond_pag = st.selectbox(
            "Condição de Pagamento",
            ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"],
        )
        status_in = st.selectbox(
            "Situação / Status",
            [
                "Em orçamento",
                "Aguardando cliente",
                "Aguardando peça",
                "Em andamento",
                "Pronto",
            ],
        )

        salvar = st.form_submit_button("💾 Salvar OS", type="primary")

        if salvar:
            conn = conectar_db()
            cursor = conn.cursor()

            if opt_cli == "-- Novo Cliente --":
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

            total_calc = (valor_peca + mao_obra) - desconto
            dt_entrada = datetime.now().strftime("%d/%m/%Y")
            dt_saida_str = dt_saida.strftime("%d/%m/%Y")

            if aparelho and defeito:
                cursor.execute(
                    """
                    INSERT INTO ordens (data_entrada, previsao_saida, cliente_id, marca, aparelho, cor, imei, senha, acessorios, defeito, valor_peca, mao_de_obra, desconto, total, status, garantia, condicao_pagamento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        dt_entrada,
                        dt_saida_str,
                        cliente_id,
                        marca,
                        aparelho,
                        cor,
                        imei,
                        senha,
                        acessorios,
                        defeito,
                        valor_peca,
                        mao_obra,
                        desconto,
                        total_calc,
                        status_in,
                        garantia,
                        cond_pag,
                    ),
                )

                if total_calc > 0:
                    cursor.execute(
                        "INSERT INTO caixa (data, tipo, descricao, valor, forma_pagamento) VALUES (?, ?, ?, ?, ?)",
                        (
                            dt_entrada,
                            "Entrada",
                            f"OS #{aparelho} - {c_nome if c_nome else 'Cliente'}",
                            total_calc,
                            cond_pag,
                        ),
                    )

                conn.commit()
                st.success("✅ Ordem de Serviço cadastrada com sucesso!")
            else:
                st.error("Preencha ao menos o Modelo e o Defeito.")

            conn.close()


# ==========================================
# PRODUTOS / ESTOQUE
# ==========================================
elif st.session_state.pagina == "📦 Produtos":
    st.subheader("📦 Lista de Produtos & Peças")

    with st.expander("➕ Cadastrar Produto"):
        with st.form("form_prod_pro", clear_on_submit=True):
            p_desc = st.text_input("Nome / Descrição (Ex: Cabo USB-C, Tela A12)")
            p_cat = st.text_input("Categoria")
            p_prec = st.number_input("Preço de Venda (R$)", min_value=0.0)
            p_qtd = st.number_input("Quantidade", min_value=1, value=1)
            btn_p = st.form_submit_button("Salvar Produto")

            if btn_p and p_desc:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO produtos (descricao, categoria, preco_venda, quantidade) VALUES (?, ?, ?, ?)",
                    (p_desc, p_cat, p_prec, p_qtd),
                )
                conn.commit()
                conn.close()
                st.success("Produto salvo!")

    conn = conectar_db()
    df_prod = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()

    if not df_prod.empty:
        for idx, row in df_prod.iterrows():
            st.markdown(
                f"""
                <div class="card-os" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <b style="color:#ffffff;">Nome:</b> {row['descricao']}<br>
                        <b style="color:#cccccc;">Valor:</b> R$ {row['preco_venda']:.2f} | <b>Qtd:</b> {row['quantidade']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Nenhum produto cadastrado.")


# ==========================================
# CLIENTES
# ==========================================
elif st.session_state.pagina == "👥 Clientes":
    st.subheader("👥 Clientes Cadastrados")
    conn = conectar_db()
    df_cli = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    st.dataframe(df_cli, use_container_width=True)


# ==========================================
# CAIXA & RELATÓRIOS
# ==========================================
elif st.session_state.pagina == "💰 Caixa & Relatórios":
    st.subheader("💰 Fluxo de Caixa")
    conn = conectar_db()
    df_cx = pd.read_sql_query("SELECT * FROM caixa ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_cx, use_container_width=True)
