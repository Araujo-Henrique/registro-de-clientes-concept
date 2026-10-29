from fastapi import APIRouter, Depends, HTTPException

from app import store
from app.routers.comum import Paginacao, igual, mesclar_e_validar, obter_ou_404
from app.schemas.cliente import ClienteBase, ClienteCreate, ClienteOut, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Clientes"])


def _exige_nome_livre(nome: str, ignorar_id: int | None = None):
    if store.achar_cliente_por_nome(nome, ignorar_id) is not None:
        raise HTTPException(status_code=409, detail="Já existe um cliente com esse nome")


@router.post("", response_model=ClienteOut, status_code=201)
def cria_cliente(cliente: ClienteCreate):
    _exige_nome_livre(cliente.nome)
    return store.clientes.inserir(cliente.model_dump())


@router.get("", response_model=list[ClienteOut])
def busca_clientes(nome: str | None = None, grupo: str | None = None, telefone: str | None = None,
                   pagina: Paginacao = Depends()):
    por_igualdade = igual(grupo=grupo, telefone=telefone)
    trecho = nome.lower() if nome else None

    def predicado(linha):
        return por_igualdade(linha) and (trecho is None or trecho in linha["nome"].lower())

    return store.clientes.listar(predicado, pagina.limit, pagina.offset)


@router.get("/{cliente_id}", response_model=ClienteOut)
def busca_cliente_por_id(cliente_id: int):
    return obter_ou_404(store.clientes, cliente_id, "Cliente")


@router.patch("/{cliente_id}", response_model=ClienteOut)
def atualiza_cliente(cliente_id: int, dados: ClienteUpdate):
    atual = obter_ou_404(store.clientes, cliente_id, "Cliente")
    mudancas = dados.model_dump(exclude_unset=True)
    if "nome" in mudancas:
        _exige_nome_livre(mudancas["nome"], ignorar_id=cliente_id)
    novo = mesclar_e_validar(ClienteBase, atual, mudancas)
    return store.clientes.atualizar(cliente_id, novo)


@router.delete("/{cliente_id}", response_model=ClienteOut)
def deleta_cliente(cliente_id: int):
    obter_ou_404(store.clientes, cliente_id, "Cliente")
    vinculos = {
        "processos de obtenção": store.processos_obt.contar(igual(cliente_id=cliente_id)),
        "processos de renovação": store.processos_ren.contar(igual(cliente_id=cliente_id)),
        "passaportes": store.passaportes.contar(igual(cliente_id=cliente_id)),
    }
    pendentes = {nome: qtd for nome, qtd in vinculos.items() if qtd}
    if pendentes:
        # o banco recusaria pela chave estrangeira; apagar em cascata destruiria o histórico
        raise HTTPException(
            status_code=409,
            detail={"mensagem": "Cliente tem registros vinculados; apague-os antes", "vinculos": pendentes},
        )
    return store.clientes.remover(cliente_id)
