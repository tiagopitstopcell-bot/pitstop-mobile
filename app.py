import streamlit as st
import sqlite3
from datetime import datetime, date

# Configuração da página com tema claro para ficar igual ao app de referência
st.set_page_config(page_title="Ordem de Serviço PRO", page_icon="🛠️", layout="wide")

# CSS Personalizado para recriar o visual das imagens
st.markdown("""
    <style>
        /* Estilo do cabeçalho azul */
        .main-header {
            background-color: #3b82f6;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        /* Cartão de OS estilo App */
        .os-card {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            color: #1f2937;
        }
        
        /* Badges de Status */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 13px;
            margin-right: 5px;
        }
        .bg-aberta { background-color: #22c55e; }
        .bg-aguardando-peca { background-color: #ef4444; }
        .bg-aguardando-cliente { background-color: #ef4444; }
        .bg-andamento { background-color: #3b82f6; }
        .bg-concluida { background-color: #f59e0b; }
        
        /* Modelo do Recibo Térmico / A4 */
        .recibo-box {
            background-color: #ffffff;
            border: 1px dashed #9ca3af;
            padding: 20px;
            font-family: 'Courier New', Courier, monospace;
            color: #000;
            max-width: 450px;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Conexão à base de dados
def get_connection():
    return sqlite3.connect('pitstop.db')

# Inicialização do Banco de Dados
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT,
            cpf_cnpj TEXT
        )
    """)
    
    # Ordens de Serviço
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            aparelho TEXT NOT NULL,
            marca TEXT,
            defeito TEXT NOT NULL,
            status TEXT NOT NULL,
            data_entrada TEXT NOT NULL,
            previsao_saida TEXT,
            data_garantia TEXT,
            condicao_pagamento TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    """)
    
    # Peças e Serviços da OS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS os_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            os_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, -- 'Peça' ou 'Serviço'
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            FOREIGN KEY (os_id) REFERENCES ordens_servico (id)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# Cabeçalho Principal
st.markdown('<div class="main-header">🛠️ Ordem de Serviço</div>', unsafe_allow_html=True)

# Menu Lateral
st.sidebar.title("Navegação")
modulo = st.sidebar.radio("Ir para:", ["Ordens de Serviço", "Nova OS", "Clientes", "Configurações da Empresa"])

# ---------------------------------------------------------
# MÓDULO 1: LISTA DE ORDENS DE SERVIÇO (CARDS)
# ---------------------------------------------------------
if modulo == "Ordens de Serviço":
    col_busca, col_add = st.columns([4, 1])
    with col_busca:
        busca = st.text_input("🔍 OS ou Cliente", placeholder="Pesquisar...")
    
    somente_andamento = st.toggle("Listar somente OS em andamento", value=True)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT os.id, os.data_entrada, os.previsao_saida, c.nome, os.status, os.aparelho
        FROM ordens_servico os
        JOIN clientes c ON os.cliente_id = c.id
        WHERE 1=1
    """
    params = []
    
    if somente_andamento:
        query += " AND os.status != 'Finalizada' AND os.status != 'Cancelada'"
    if busca:
        query += " AND (c.nome LIKE ? OR os.id LIKE ? OR os.aparelho LIKE ?)"
        params.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%"])
        
    query += " ORDER BY os.id DESC"
    cursor.execute(query, params)
    lista_os = cursor.fetchall()
    conn.close()
    
    for os_item in lista_os:
        os_id, dt_in, dt_out, cliente, status, aparelho = os_item
        
        # Seleção de classe CSS para as cores das badges de status
        badge_class = "bg-andamento"
        if status == "Aguardando cliente":
            badge_class = "bg-aguardando-cliente"
        elif status == "Aguardando peça":
            badge_class = "bg-aguardando-peca"
        elif status == "Aberta":
            badge_class = "bg-aberta"
        elif status == "Finalizada":
            badge_class = "bg-concluida"
            
        with st.container():
            st.markdown(f"""
                <div class="os-card">
                    <b>OS: {os_id}</b><br>
                    <small><b>Data Entrada:</b> {dt_in}</small><br>
                    <small><b>Previsão Saída:</b> {dt_out or 'N/A'}</small><br>
                    <b>Cliente:</b> {cliente} ({aparelho})<br><br>
                    <span class="badge {badge_class}">{status}</span>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("🖨️ Imprimir OS", key=f"imp_{os_id}"):
                    st.session_state['imprimir_os_id'] = os_id
            with c2:
                if st.button("✏️ Editar/Itens", key=f"edt_{os_id}"):
                    st.session_state['editar_os_id'] = os_id

    # Modal / Secção de Impressão (Geração de Recibo/A4)
    if 'imprimir_os_id' in st.session_state and st.session_state['imprimir_os_id']:
        os_imp_id = st.session_state['imprimir_os_id']
        st.divider()
        st.subheader(f"📄 Impressão da OS #{os_imp_id}")
        
        tipo_impressao = st.radio("Qual tipo de impressão deseja?", ["Térmica (80mm)", "Impressão A4"], horizontal=True)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT os.id, os.data_entrada, os.previsao_saida, os.data_garantia, os.aparelho, os.marca, os.defeito, os.condicao_pagamento, c.nome, c.telefone, c.endereco, c.cpf_cnpj
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            WHERE os.id = ?
        """, (os_imp_id,))
        dados = cursor.fetchone()
        
        cursor.execute("SELECT tipo, descricao, valor FROM os_itens WHERE os_id = ?", (os_imp_id,))
        itens = cursor.fetchall()
        conn.close()
        
        if dados:
            total_os = sum([i[2] for i in itens]) if itens else 0.0
            
            # Recibo visual no estilo da imagem 3
            st.markdown(f"""
                <div class="recibo-box">
                    <center>
                        <h3>PitStopCell</h3>
                        <p><small>Assistência Técnica Especializada</small></p>
                        <hr>
                        <h4>Ordem de Serviço {dados[0]}</h4>
                    </center>
                    <p><b>Garantia Até:</b> {dados[3] or 'N/A'}</p>
                    <p><b>Data Entrada:</b> {dados[1]} &nbsp;&nbsp; <b>Previsão Saída:</b> {dados[2] or 'N/A'}</p>
                    <hr>
                    <p><b>Cliente:</b> {dados[8]}</p>
                    <p><b>Telefone:</b> {dados[9] or 'N/A'}</p>
                    <p><b>Modelo:</b> {dados[4]} &nbsp;&nbsp; <b>Marca:</b> {dados[5] or 'N/A'}</p>
                    <p><b>Reclamação/Defeito:</b> {dados[6]}</p>
                    <hr>
                    <b>Itens / Serviços:</b><br>
                    {"".join([f"<p>- {it[1]} ({it[0]}): R$ {it[2]:.2f}</p>" for it in itens]) if itens else "<p>Nenhum item adicionado.</p>"}
                    <hr>
                    <h4>Valor Total: R$ {total_os:.2f}</h4>
                    <p><small>Condição de Pagamento: {dados[7] or 'À vista'}</small></p>
                </div>
            """, unsafe_allow_html=True)
            
        if st.button("Fechar Impressão"):
            st.session_state['imprimir_os_id'] = None
            st.rerun()

# ---------------------------------------------------------
# MÓDULO 2: NOVA ORDEM DE SERVIÇO / ADICIONAR PEÇAS
# ---------------------------------------------------------
elif modulo == "Nova OS":
    st.subheader("📝 Abertura de Nova OS")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
    clientes = cursor.fetchall()
    conn.close()
    
    if not clientes:
        st.warning("Cadastre primeiro um cliente no menu 'Clientes'.")
    else:
        dict_clientes = {f"{c[1]} (ID: {c[0]})": c[0] for c in clientes}
        
        with st.form("form_nova_os"):
            cliente_sel = st.selectbox("Selecione o Cliente *", options=list(dict_clientes.keys()))
            c1, c2 = st.columns(2)
            with c1:
                dt_entrada = st.date_input("Data Entrada", value=date.today())
                aparelho = st.text_input("Modelo do Aparelho *", placeholder="Ex: Moto G7")
            with c2:
                dt_saida = st.date_input("Previsão Saída", value=date.today())
                marca = st.text_input("Marca", placeholder="Ex: Motorola")
                
            defeito = st.text_area("Defeito Relatado / Reclamação *")
            status = st.selectbox("Status Inicial", ["Aberta", "Aguardando peça", "Aguardando cliente", "Em andamento"])
            
            submeter = st.form_submit_button("Criar e Avançar para Itens/Garantia")
            
            if submeter:
                if not aparelho.strip() or not defeito.strip():
                    st.error("Preencha o modelo do aparelho e o defeito!")
                else:
                    c_id = dict_clientes[cliente_sel]
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO ordens_servico (cliente_id, aparelho, marca, defeito, status, data_entrada, previsao_saida)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (c_id, aparelho, marca, defeito, status, dt_entrada.strftime("%d/%m/%Y"), dt_saida.strftime("%d/%m/%Y")))
                    conn.commit()
                    new_id = cursor.lastrowid
                    conn.close()
                    st.success(f"OS #{new_id} gerada com sucesso!")

# ---------------------------------------------------------
# MÓDULO 3: CLIENTES
# ---------------------------------------------------------
elif modulo == "Clientes":
    st.subheader("👥 Cadastro de Clientes")
    with st.form("form_cli", clear_on_submit=True):
        nome = st.text_input("Nome Completo *")
        tel = st.text_input("Telefone")
        end = st.text_input("Endereço Completo")
        cpf = st.text_input("CPF/CNPJ")
        
        if st.form_submit_button("Salvar Cliente"):
            if nome.strip():
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO clientes (nome, telefone, endereco, cpf_cnpj) VALUES (?, ?, ?, ?)", (nome, tel, end, cpf))
                conn.commit()
                conn.close()
                st.success("Cliente guardado com sucesso!")
            else:
                st.error("O Nome é obrigatório.")
