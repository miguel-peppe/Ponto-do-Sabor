from core.imports import *
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash

# Caminho do seu banco principal
DB_PATH = r"C:\Users\pedro\OneDrive\Área de Trabalho\sat varejo flask\app\database\schema.db"


# -----------------------------
# CONEXÃO GENÉRICA
# -----------------------------
def get_connection(db_path: str = DB_PATH):
    """
    Abre uma conexão com o banco principal (schema.db por padrão).
    Configura row_factory para retornar sqlite3.Row (acesso por nome de coluna).
    """
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def get_some_connection(table_name: str = 'funcionario', db_path: str = DB_PATH):
    """
    Abre a conexão com o banco e verifica se a tabela informada existe.
    Retorna a conexão aberta se a tabela existir, senão levanta erro.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Usa parâmetro para evitar SQL injection
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?;
    """, (table_name,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        raise RuntimeError(f"Tabela '{table_name}' não encontrada no banco '{db_path}'.")

    return conn  # lembre de fechar depois de usar: conn.close()


# -----------------------------
# TABELA FUNCIONARIO
# -----------------------------
def db_init_funcionario():
    """
    Cria a tabela 'funcionario' no schema.db, se ainda não existir.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funcionario (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                nome             TEXT NOT NULL,
                cpf              TEXT NOT NULL UNIQUE,
                cargo            TEXT NOT NULL,
                senha_hash       TEXT NOT NULL,
                data_contratacao DATE NOT NULL,
                ativo            INTEGER
            )
        ''')
        conn.commit()


def add_funcionario(nome, cpf: int, cargo, senha_hash, data_contratacao=None, ativo=1):
    """
    Insere um novo funcionário na tabela 'funcionario'.
    """
    if data_contratacao is None:
        data_contratacao = date.today().isoformat()  # YYYY-MM-DD

    # senha_hash = generate_password_hash(senha_hash)  # já deve vir hash da senha
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO funcionario (nome, cpf, cargo, senha_hash, data_contratacao, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, cpf, cargo, senha_hash, data_contratacao, ativo))
    conn.commit()
    conn.close()


# -----------------------------
# TABELA NOTES (anotações)
# -----------------------------
def db_init_note():
    """
    Cria a tabela 'notes' no schema.db, se ainda não existir.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                conteudo  TEXT NOT NULL,
                data_mod  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ativo     INTEGER NOT NULL DEFAULT 1
            )
        ''')
        conn.commit()


def addNote(conteudo, db_path: str = DB_PATH):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (conteudo, data_mod, ativo) VALUES (?, CURRENT_TIMESTAMP, 1)",
            (conteudo,)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

# -----------------------------
# EXECUÇÃO GENÉRICA DE SQL
# -----------------------------
def executar_sql(comando, params=(), db_path: str = DB_PATH):
    """
    Executa qualquer comando SQL no banco informado (por padrão schema.db).
    - Se for SELECT, retorna lista de dicts.
    - Caso contrário, faz commit e retorna status e linhas afetadas.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(comando, params)

        if comando.strip().lower().startswith("select"):
            rows = cur.fetchall()
            # retorna lista de dicts
            return [dict(r) for r in rows]
        else:
            conn.commit()
            return {'status': 'ok', 'linhas_afetadas': cur.rowcount}
    except sqlite3.Error as e:
        # logue o erro para depuração
        print("SQLite error:", e)
        return {'erro': str(e)}
    finally:
        conn.close()

# -----------------------------
# FUNÇÃO PARA INICIAR TUDO
# -----------------------------
def db_init_all():
    """
    Chama todas as funções de criação de tabela.
    Use isso quando subir a aplicação, por exemplo.
    """
    db_init_funcionario()
    db_init_note()
    # se criar mais tabelas no futuro, adiciona aqui


# Exemplo rápido de uso quando rodar esse arquivo direto
if __name__ == "__main__":
    db_init_all()
    print("Tabelas criadas/validadas com sucesso em schema.db.")
