from fastapi import APIRouter, Depends

from app import store
from app.enums import SituacaoPassaporte
from app.routers.comum import Paginacao, igual, mesclar_e_validar, obter_ou_404
from app.schemas.passaporte import (PassaporteBase, PassaporteCreate, PassaporteOut,
                                    PassaporteUpdate)

router = APIRouter(prefix="/passaportes", tags=["Passaportes"])


@router.post("", response_model=PassaporteOut, status_code=201)
def cria_passaporte(passaporte: PassaporteCreate):
    obter_ou_404(store.clientes, passaporte.cliente_id, "Cliente")
    return store.passaportes.inserir(passaporte.model_dump())


@router.get("", response_model=list[PassaporteOut])
def busca_passaportes(cliente_id: int | None = None, situacao: SituacaoPassaporte | None = None,
                      pagina: Paginacao = Depends()):
    predicado = igual(cliente_id=cliente_id, situacao=situacao)
    return store.passaportes.listar(predicado, pagina.limit, pagina.offset)


@router.get("/{passaporte_id}", response_model=PassaporteOut)
def busca_passaporte(passaporte_id: int):
    return obter_ou_404(store.passaportes, passaporte_id, "Passaporte")


@router.patch("/{passaporte_id}", response_model=PassaporteOut)
def atualiza_passaporte(passaporte_id: int, dados: PassaporteUpdate):
    atual = obter_ou_404(store.passaportes, passaporte_id, "Passaporte")
    novo = mesclar_e_validar(PassaporteBase, atual, dados.model_dump(exclude_unset=True))
    return store.passaportes.atualizar(passaporte_id, novo)


@router.delete("/{passaporte_id}", response_model=PassaporteOut)
def deleta_passaporte(passaporte_id: int):
    obter_ou_404(store.passaportes, passaporte_id, "Passaporte")
    return store.passaportes.remover(passaporte_id)
