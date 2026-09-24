
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
            telefone TEXT
        )
    """
    )

    # Tabela de Ordens de Serviço
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            aparelho TEXT NOT NULL,
            defeito TEXT NOT NULL,
            status TEXT DEFAULT 'Em andamento',
            valor REAL DEFAULT 0.0,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
