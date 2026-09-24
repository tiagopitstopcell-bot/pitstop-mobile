import sqlite3
import streamlit as st
from database import init_db

# Configuração da página para estilo mobile
st.set_page_config(
    page_title="Ordem de Serviço Pró", page_icon="🛠️", layout="centered"
)

# Inicializa as tabelas do banco de dados
init_db()


# Função para buscar ordens no SQLite
def buscar_ordens(termo="", somente_andamento=False):
    conn = sqlite3.connect("pitstop.db")
    cursor = conn.cursor()

    query = """
        SELECT o.id, c.nome, o.aparelho, o.defeito, o.status, o.valor
        FROM ordens o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE 1=1
    """
    params = []

    if termo:
        query += " AND (c.nome LIKE ? OR o.aparelho LIKE ? OR o.defeito LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%", f"%{termo}%"])

    if somente_andamento:
        query += " AND o.status = 'Em andamento'"

    query += " ORDER BY o.id DESC"

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    return resultados


# --- INTERFACE ---

st.title("🛠️ Ordem de Serviço")

# 1. Campo de busca e filtro
busca = st.text_input("🔍 OS ou Cliente", placeholder="Pesquisar...")
somente_andamento = st.toggle("Listar somente OS em andamento", value=True)

# 2. Carregar dados
ordens = buscar_ordens(busca, somente_andamento)

# 3. Lista de resultados
st.markdown("---")
if ordens:
    for os_id, cliente, aparelho, defeito, status, valor in ordens:
        with st.container():
            st.subheader(
                f"OS #{os_id} - {cliente if cliente else 'Cliente não identificado'}"
            )
            st.caption(f"📱 **Aparelho:** {aparelho}")
            st.write(f"📝 **Defeito:** {defeito}")
            st.write(f"💰 **Valor:** R$ {valor:.2f}")

            # Badge de status
            if status == "Em andamento":
                st.warning(f"Status: {status}")
            else:
                st.success(f"Status: {status}")

            st.divider()
else:
    st.info("Nenhuma ordem de serviço encontrada.")
