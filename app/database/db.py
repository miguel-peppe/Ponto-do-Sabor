from core.imports import *
import sqlite3
from datetime import date

def get_connect():
    conn = sqlite3.connect('funcionarios.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def get_connect_dyn(tablename):
    conn = sqlite3.connect(tablename, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def db_init():
    with get_connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funcionario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                cargo TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                data_contratacao DATE NOT NULL,
                ativo INTEGER
            )
        ''')
        conn.commit()

def add_funcionario(nome, cpf : int, cargo, senha_hash, data_contratacao=None, ativo=1):
    if data_contratacao is None:
        data_contratacao = date.today().isoformat()  # YYYY-MM-DD

    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO funcionario (nome, cpf, cargo, senha_hash, data_contratacao, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, cpf, cargo, senha_hash, data_contratacao, ativo))
    conn.commit()
    conn.close()

def get_connect_notes():
    return get_connect_dyn('notes.db')

def db_init_note():
    with get_connect_notes() as conn:
        cur = conn.cursor()
        # data_mod com DEFAULT CURRENT_TIMESTAMP e ativo com DEFAULT 1
        cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                conteudo  TEXT NOT NULL,
                data_mod  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ativo     INTEGER NOT NULL DEFAULT 1
            )
        ''')
        conn.commit()

def addNote(conteudo, db_path='notes.db'):
    # Garante data_mod e ativo
    return executar_sql(
        "INSERT INTO notes (conteudo, data_mod, ativo) VALUES (?, CURRENT_TIMESTAMP, 1)",
        (conteudo,),
        db_path=db_path
    )


def executar_sql(comando, params=(), db_path='notes.db'):
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
        
def initPedido():
    with get_connect_notes() as conn:
        cur = conn.cursor()
        #
        cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomeProduto TEXT NOT NULL,
                data_mod TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                preco REAL,
                ativo INTEGER NOT NULL DEFAULT 1
            )
        ''')
        conn.commit()
