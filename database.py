import sqlite3


def init_db():
    conn = sqlite3.connect("pitstop.db")
    cursor = conn.cursor()

    # Tabela de Clientes
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            whatsapp TEXT,
            cpf_cnpj TEXT,
            endereco TEXT
        )
    """
    )

    # Tabela de Produtos / Estoque
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            descricao TEXT NOT NULL,
            categoria TEXT,
            quantidade INTEGER DEFAULT 0,
            custo REAL DEFAULT 0.0,
            preco_venda REAL DEFAULT 0.0
        )
    """
    )

    # Tabela de Ordens de Serviço (Ampliada com campos do modelo)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_entrada TEXT NOT NULL,
            previsao_saida TEXT,
            cliente_id INTEGER,
            marca TEXT,
            aparelho TEXT NOT NULL,
            cor TEXT,
            imei TEXT,
            senha TEXT,
            acessorios TEXT,
            defeito TEXT NOT NULL,
            diagnostico TEXT,
            peca_id INTEGER,
            valor_peca REAL DEFAULT 0.0,
            mao_de_obra REAL DEFAULT 0.0,
            desconto REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            status TEXT DEFAULT 'Em orçamento',
            garantia TEXT,
            condicao_pagamento TEXT,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (peca_id) REFERENCES produtos (id)
        )
    """
    )

    # Tabela de Caixa
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            forma_pagamento TEXT
        )
    """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
