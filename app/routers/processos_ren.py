from fastapi import APIRouter, Depends

from app import store
from app.enums import Consulado, SituacaoREN
from app.routers.comum import Paginacao, contem, igual, mesclar_e_validar, obter_ou_404
from app.schemas.processo_ren import (ProcessoRENBase, ProcessoRENCreate, ProcessoRENOut,
                                      ProcessoRENUpdate)

router = APIRouter(prefix="/processos-ren", tags=["Processos de renovação (REN)"])


@router.post("", response_model=ProcessoRENOut, status_code=201)
def cria_processo_ren(processo: ProcessoRENCreate):
    obter_ou_404(store.clientes, processo.cliente_id, "Cliente")
    return store.processos_ren.inserir(processo.model_dump())


@router.get("", response_model=list[ProcessoRENOut])
def busca_processos_ren(cliente_id: int | None = None, consulado: Consulado | None = None,
                        situacao: SituacaoREN | None = None, codigo_ds160: str | None = None,
                        pagina: Paginacao = Depends()):
    predicado = igual(cliente_id=cliente_id, consulado=consulado, situacao=situacao)
    por_codigo = contem("codigo_ds160", codigo_ds160)
    return store.processos_ren.listar(lambda linha: predicado(linha) and por_codigo(linha), pagina.limit, pagina.offset)


@router.get("/{processo_id}", response_model=ProcessoRENOut)
def busca_processo_ren(processo_id: int):
    return obter_ou_404(store.processos_ren, processo_id, "Processo de renovação")


@router.patch("/{processo_id}", response_model=ProcessoRENOut)
def atualiza_processo_ren(processo_id: int, dados: ProcessoRENUpdate):
    atual = obter_ou_404(store.processos_ren, processo_id, "Processo de renovação")
    novo = mesclar_e_validar(ProcessoRENBase, atual, dados.model_dump(exclude_unset=True))
    return store.processos_ren.atualizar(processo_id, novo)


@router.delete("/{processo_id}", response_model=ProcessoRENOut)
def deleta_processo_ren(processo_id: int):
    obter_ou_404(store.processos_ren, processo_id, "Processo de renovação")
    return store.processos_ren.remover(processo_id)
