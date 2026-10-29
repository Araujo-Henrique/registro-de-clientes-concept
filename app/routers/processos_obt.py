from fastapi import APIRouter, Depends

from app import store
from app.enums import ConsuladoOBT, Monitoramento, SituacaoOBT
from app.routers.comum import Paginacao, contem, igual, mesclar_e_validar, obter_ou_404
from app.schemas.processo_obt import (ProcessoOBTBase, ProcessoOBTCreate, ProcessoOBTOut,
                                      ProcessoOBTUpdate)

router = APIRouter(prefix="/processos-obt", tags=["Processos de obtenção (OBT)"])


def _confere_funcionario(funcionario_id: int | None):
    if funcionario_id is not None:
        obter_ou_404(store.funcionarios, funcionario_id, "Funcionário")


@router.post("", response_model=ProcessoOBTOut, status_code=201)
def cria_processo_obt(processo: ProcessoOBTCreate):
    obter_ou_404(store.clientes, processo.cliente_id, "Cliente")
    _confere_funcionario(processo.orientacao_por_id)
    return store.processos_obt.inserir(processo.model_dump())


@router.get("", response_model=list[ProcessoOBTOut])
def busca_processos_obt(cliente_id: int | None = None, consulado: ConsuladoOBT | None = None,
                        situacao: SituacaoOBT | None = None,
                        monitoramento: Monitoramento | None = None, codigo_ds160: str | None = None,
                        pagina: Paginacao = Depends()):
    predicado = igual(cliente_id=cliente_id, consulado=consulado, situacao=situacao,
                      monitoramento=monitoramento)
    por_codigo = contem("codigo_ds160", codigo_ds160)
    return store.processos_obt.listar(lambda linha: predicado(linha) and por_codigo(linha), pagina.limit, pagina.offset)


@router.get("/{processo_id}", response_model=ProcessoOBTOut)
def busca_processo_obt(processo_id: int):
    return obter_ou_404(store.processos_obt, processo_id, "Processo de obtenção")


@router.patch("/{processo_id}", response_model=ProcessoOBTOut)
def atualiza_processo_obt(processo_id: int, dados: ProcessoOBTUpdate):
    atual = obter_ou_404(store.processos_obt, processo_id, "Processo de obtenção")
    mudancas = dados.model_dump(exclude_unset=True)
    _confere_funcionario(mudancas.get("orientacao_por_id"))
    novo = mesclar_e_validar(ProcessoOBTBase, atual, mudancas)
    return store.processos_obt.atualizar(processo_id, novo)


@router.delete("/{processo_id}", response_model=ProcessoOBTOut)
def deleta_processo_obt(processo_id: int):
    obter_ou_404(store.processos_obt, processo_id, "Processo de obtenção")
    return store.processos_obt.remover(processo_id)
