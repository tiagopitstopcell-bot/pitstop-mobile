import sqlite3

def init_db():
    conn = sqlite3.connect('pitstop.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
