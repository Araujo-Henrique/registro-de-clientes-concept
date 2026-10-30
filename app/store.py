"""Acesso às tabelas do PostgreSQL.

Cada Tabela expõe as mesmas operações de antes (inserir, obter, listar, ...), então os routers não
sabem que agora existe um banco. Nomes de tabela e coluna vêm sempre do nosso código, nunca do usuário,
e mesmo assim entram na consulta como identificadores (sql.Identifier); os valores vão como parâmetros
(%s), nunca concatenados no texto: é isso que impede SQL injection.
"""
from enum import Enum

from psycopg import sql

from app import db


def _valor(valor):
    # os enums da API são str; o banco recebe o texto puro
    return valor.value if isinstance(valor, Enum) else valor


def _lista(pedacos):
    return sql.SQL(", ").join(pedacos)


class Tabela:
    def __init__(self, nome: str):
        self._tabela = sql.Identifier(nome)

    def _executa(self, consulta, parametros=(), todas=False):
        with db.conexao() as conn:
            cursor = conn.execute(consulta, parametros)
            return cursor.fetchall() if todas else cursor.fetchone()

    def _filtro(self, igual: dict | None, contem: dict | None):
        """WHERE montado a partir de dicionários; valores None são ignorados (filtro não informado)."""
        condicoes, parametros = [], []
        for campo, valor in (igual or {}).items():
            if valor is not None:
                condicoes.append(sql.SQL("{} = %s").format(sql.Identifier(campo)))
                parametros.append(_valor(valor))
        for campo, trecho in (contem or {}).items():
            if trecho is not None:
                # position() em vez de LIKE: o trecho pode ter % ou _ sem virar curinga
                condicoes.append(sql.SQL("position(lower(%s) in lower({})) > 0").format(sql.Identifier(campo)))
                parametros.append(trecho)
        if not condicoes:
            return sql.SQL(""), parametros
        return sql.SQL(" WHERE ") + sql.SQL(" AND ").join(condicoes), parametros

    def inserir(self, dados: dict) -> dict:
        consulta = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
            self._tabela,
            _lista(sql.Identifier(c) for c in dados),
            _lista(sql.Placeholder() for _ in dados),
        )
        return self._executa(consulta, [_valor(v) for v in dados.values()])

    def obter(self, id: int) -> dict | None:
        consulta = sql.SQL("SELECT * FROM {} WHERE id = %s").format(self._tabela)
        return self._executa(consulta, [id])

    def listar(self, igual: dict | None = None, contem: dict | None = None,
               limit: int = 50, offset: int = 0) -> list[dict]:
        where, parametros = self._filtro(igual, contem)
        consulta = sql.SQL("SELECT * FROM {}{} ORDER BY id LIMIT %s OFFSET %s").format(self._tabela, where)
        return self._executa(consulta, [*parametros, limit, offset], todas=True)

    def contar(self, igual: dict | None = None) -> int:
        where, parametros = self._filtro(igual, None)
        consulta = sql.SQL("SELECT count(*) AS total FROM {}{}").format(self._tabela, where)
        return self._executa(consulta, parametros)["total"]

    def atualizar(self, id: int, dados: dict, se: dict | None = None) -> dict | None:
        """Grava só os campos de `dados`. Com `se`, só grava se esses campos ainda tiverem os valores
        informados (nenhuma outra pessoa mexeu no meio do caminho); sem linha alterada devolve None."""
        sets = _lista(sql.SQL("{} = %s").format(sql.Identifier(c)) for c in dados)
        condicoes = [sql.SQL("id = %s")]
        parametros = [*(_valor(v) for v in dados.values()), id]
        for campo, valor in (se or {}).items():
            # IS NOT DISTINCT FROM trata NULL como valor comparável (NULL = NULL daria falso)
            condicoes.append(sql.SQL("{} IS NOT DISTINCT FROM %s").format(sql.Identifier(campo)))
            parametros.append(_valor(valor))
        consulta = sql.SQL("UPDATE {} SET {} WHERE {} RETURNING *").format(
            self._tabela, sets, sql.SQL(" AND ").join(condicoes))
        return self._executa(consulta, parametros)

    def remover(self, id: int) -> dict | None:
        consulta = sql.SQL("DELETE FROM {} WHERE id = %s RETURNING *").format(self._tabela)
        return self._executa(consulta, [id])


clientes = Tabela("clientes")
processos_obt = Tabela("processos_obt")
processos_ren = Tabela("processos_ren")
passaportes = Tabela("passaportes")
funcionarios = Tabela("funcionarios")


def achar_cliente_por_nome(nome: str, ignorar_id: int | None = None) -> dict | None:
    # mesma regra do índice único do banco (LOWER(nome)): sem diferenciar maiúscula
    consulta = "SELECT * FROM clientes WHERE lower(nome) = lower(%s) AND id IS DISTINCT FROM %s LIMIT 1"
    with db.conexao() as conn:
        return conn.execute(consulta, [nome, ignorar_id]).fetchone()
