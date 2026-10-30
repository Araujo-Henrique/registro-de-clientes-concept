from fastapi import HTTPException, Query
from pydantic import BaseModel, ValidationError

from app.store import Tabela


class Paginacao:
    def __init__(self, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
        self.limit = limit
        self.offset = offset


def obter_ou_404(tabela: Tabela, id: int, rotulo: str) -> dict:
    linha = tabela.obter(id)
    if linha is None:
        raise HTTPException(status_code=404, detail=f"{rotulo} não encontrado")
    return linha


def mesclar_e_validar(modelo: type[BaseModel], atual: dict, mudancas: dict) -> dict:
    """Aplica o PATCH sobre o registro atual e valida o resultado inteiro.

    Assim as regras que olham vários campos (ex.: orientação agendada exige data) enxergam o estado
    final, e não só o que veio no PATCH.
    """
    # campos geridos por rotas próprias (ex.: codigo_ds160) ficam fora da validação do PATCH
    candidato = {**{k: v for k, v in atual.items() if k in modelo.model_fields}, **mudancas}
    try:
        return modelo.model_validate(candidato).model_dump()
    except ValidationError as erro:
        raise HTTPException(
            status_code=422,
            detail=erro.errors(include_url=False, include_context=False, include_input=False),
        )
