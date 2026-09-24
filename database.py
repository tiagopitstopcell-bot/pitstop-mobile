import sqlite3


def init_db():
    conn = sqlite3.connect("pitstop.db")
    cursor = conn.cursor()

    # Tabela de Clientes com Endereço, E-mail e Observações
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            cpf_cnpj TEXT,
            endereco TEXT,
            email TEXT,
            observacoes TEXT
        )
    """
    )

    # Tabela de Ordens de Serviço
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_entrada TEXT,
            previsao_saida TEXT,
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
    """
    )

    # Tabela de Produtos / Estoque
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT,
            preco_venda REAL,
            quantidade INTEGER
        )
    """
    )

    # Tabela de Fluxo de Caixa
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo TEXT,
            descricao TEXT,
            valor REAL,
            forma_pagamento TEXT
        )
    """
    )

    conn.commit()
    conn.close()
