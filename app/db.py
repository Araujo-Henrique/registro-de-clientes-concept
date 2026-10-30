"""Conexão com o PostgreSQL.

Um pool mantém algumas conexões abertas e as empresta a cada operação: abrir uma conexão nova a cada
requisição seria lento. O endereço do banco (com a senha) vem da variável de ambiente DATABASE_URL,
nunca do código.
"""
import os
from contextlib import AbstractContextManager

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

_pool: ConnectionPool | None = None


def abrir(url: str | None = None) -> bool:
    """Abre o pool (se ainda não estiver aberto). Devolve True se foi esta chamada que abriu."""
    global _pool
    if _pool is not None:
        return False
    url = url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Defina a variável de ambiente DATABASE_URL (veja o .env.example)")
    # dict_row: cada linha volta como dicionário {coluna: valor}, o formato que os routers esperam
    _pool = ConnectionPool(url, min_size=1, max_size=10, kwargs={"row_factory": dict_row}, open=True)
    return True


def fechar():
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def conexao() -> AbstractContextManager[Connection]:
    """Empresta uma conexão: confirma (commit) ao sair do bloco, ou desfaz (rollback) se der erro."""
    if _pool is None:
        raise RuntimeError("O pool de conexões não foi aberto")
    return _pool.connection()
