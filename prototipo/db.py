"""Conexão e execução de queries no PostgreSQL."""
import psycopg2
from psycopg2.extras import RealDictCursor


def conectar(host: str, port: int, dbname: str, user: str, password: str):
    """Abre conexão com o PostgreSQL e retorna o objeto de conexão."""
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        cursor_factory=RealDictCursor,
    )


def executar_query(conn, sql: str, params=None):
    """Executa SQL e retorna (colunas, linhas).

    Para comandos sem resultset (INSERT/UPDATE/DELETE/DDL), retorna ([], []).
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        if cur.description:
            cols = [d.name for d in cur.description]
            rows = [list(r.values()) for r in cur.fetchall()]
            return cols, rows
        conn.commit()
        return [], []
