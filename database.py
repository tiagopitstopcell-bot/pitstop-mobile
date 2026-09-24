import sqlite3


def init_db():
  conn = sqlite3.connect('pitstop.db')
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_loja TEXT,
            telefone TEXT,
            endereco TEXT,
            cidade TEXT,
            cnpj TEXT,
            link_google TEXT
        )
    """)

  cursor.execute('SELECT COUNT(*) FROM configuracoes')
  if cursor.fetchone()[0] == 0:
    cursor.execute("""
            INSERT INTO configuracoes (nome_loja, telefone, endereco, cidade, cnpj, link_google)
            VALUES ('PitStop Cell', '(48) 99999-9999', 'Rua Principal, 100', 'Palhoça - SC', '00.000.000/0001-00', 'https://maps.google.com/?q=PitStop+Cell')
        """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            cpf_cnpj TEXT,
            endereco TEXT,
            email TEXT,
            data_nascimento TEXT,
            observacoes TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_entrada TEXT,
            previsao_saida TEXT,
            data_entrega TEXT,
            cliente_id INTEGER,
            marca TEXT,
            aparelho TEXT,
            cor TEXT,
            imei TEXT,
            senha TEXT,
            acessorios TEXT,
            defeito TEXT,
            valor_peca REAL,
            mao_de_obra REAL,
            desconto REAL,
            total REAL,
            status TEXT DEFAULT 'Em orçamento',
            garantia TEXT,
            condicao_pagamento TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)

  cursor.execute('PRAGMA table_info(ordens)')
  colunas = [col[1] for col in cursor.fetchall()]
  if 'data_entrega' not in colunas:
    cursor.execute('ALTER TABLE ordens ADD COLUMN data_entrega TEXT')

  # Tabela de Produtos com Fornecedor
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT,
            fornecedor TEXT,
            preco_venda REAL,
            quantidade INTEGER
        )
    """)

  cursor.execute('PRAGMA table_info(produtos)')
  colunas_prod = [col[1] for col in cursor.fetchall()]
  if 'fornecedor' not in colunas_prod:
    cursor.execute('ALTER TABLE produtos ADD COLUMN fornecedor TEXT')

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo TEXT,
            descricao TEXT,
            valor REAL,
            forma_pagamento TEXT
        )
    """)

  conn.commit()
  conn.close()
