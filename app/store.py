"""Armazenamento em memória.

Cada tabela guarda dicionários por id, como linhas de uma tabela SQL. Os routers só falam com
esta camada, então a integração com o PostgreSQL consiste em trocá-la, sem mexer nas rotas.
"""
from collections.abc import Callable


class Tabela:
    def __init__(self):
        self.limpar()

    def limpar(self):
        self._linhas: dict[int, dict] = {}
        self._proximo_id = 1

    def inserir(self, dados: dict) -> dict:
        linha = {"id": self._proximo_id, **dados}
        self._linhas[linha["id"]] = linha
        self._proximo_id += 1
        return linha

    def obter(self, id: int) -> dict | None:
        return self._linhas.get(id)

    def listar(self, predicado: Callable[[dict], bool] = lambda linha: True,
               limit: int = 50, offset: int = 0) -> list[dict]:
        encontrados = [linha for linha in self._linhas.values() if predicado(linha)]
        return encontrados[offset:offset + limit]

    def contar(self, predicado: Callable[[dict], bool]) -> int:
        return sum(1 for linha in self._linhas.values() if predicado(linha))

    def atualizar(self, id: int, dados: dict) -> dict:
        linha = self._linhas[id]
        linha.update(dados)
        return linha

    def remover(self, id: int) -> dict | None:
        return self._linhas.pop(id, None)


clientes = Tabela()
processos_obt = Tabela()
processos_ren = Tabela()
passaportes = Tabela()
funcionarios = Tabela()

_FUNCIONARIOS = [
    ("Gabriel Vieira", True),
    ("Marcio Conde", True),
    ("Henrique Araujo", True),
    ("Roger Cardoso", False),
    ("Thiago Matos", False),
    ("Esther Matos", False),
    ("Joao Banks", False),
]


def reiniciar():
    """Zera tudo e recria os funcionários (usado ao iniciar e nos testes)."""
    for tabela in (clientes, processos_obt, processos_ren, passaportes, funcionarios):
        tabela.limpar()
    for nome, ativo in _FUNCIONARIOS:
        funcionarios.inserir({"nome": nome, "ativo": ativo})


def achar_cliente_por_nome(nome: str, ignorar_id: int | None = None) -> dict | None:
    # mesma regra do índice único do banco: sem diferenciar maiúscula
    alvo = nome.lower()
    for linha in clientes.listar(limit=10**9):
        if linha["nome"].lower() == alvo and linha["id"] != ignorar_id:
            return linha
    return None


reiniciar()
