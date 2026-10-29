"""Rotas do DS-160 de um processo (códigos dos formulários e notas), iguais para OBT e REN.

O PATCH geral do processo não mexe nestas colunas: aqui cada operação altera só o que pediu,
em vez de sobrescrever o texto inteiro.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.routers.comum import obter_ou_404
from app.schemas.ds160 import (CodigoDS160, CodigoDS160Out, NotaAdicionar, NotaEditar, SolicitanteUpdate,
                               le_linhas, monta_linhas, tem_linha_de_codigo)
from app.store import Tabela


def _acha(entradas: list[CodigoDS160Out], codigo: str) -> int | None:
    for posicao, entrada in enumerate(entradas):
        if entrada.codigo.upper() == codigo.upper():
            return posicao
    return None


def _recusa_linha_de_codigo(texto: str):
    if tem_linha_de_codigo(texto):
        raise HTTPException(
            status_code=422,
            detail="Linhas que começam com AA00 são códigos; use a rota /codigos-ds160",
        )


def rotas_ds160(prefixo: str, tabela: Tabela, modelo_out: type[BaseModel], rotulo: str, tag: str) -> APIRouter:
    router = APIRouter(prefix=prefixo, tags=[tag])

    def processo_ou_404(processo_id: int) -> dict:
        return obter_ou_404(tabela, processo_id, rotulo)

    # ---------- códigos: um por formulário, identificado pelo código ----------

    @router.post("/{processo_id}/codigos-ds160", response_model=modelo_out, status_code=201)
    def adiciona_codigo(processo_id: int, dados: CodigoDS160):
        entradas = le_linhas(processo_ou_404(processo_id).get("codigo_ds160"))
        if _acha(entradas, dados.codigo) is not None:
            raise HTTPException(status_code=409, detail="Esse código já está registrado neste processo")
        entradas.append(CodigoDS160Out(codigo=dados.codigo, solicitante=dados.solicitante))
        return tabela.atualizar(processo_id, {"codigo_ds160": monta_linhas(entradas)})

    @router.patch("/{processo_id}/codigos-ds160/{codigo}", response_model=modelo_out)
    def edita_codigo(processo_id: int, codigo: str, dados: SolicitanteUpdate):
        entradas = le_linhas(processo_ou_404(processo_id).get("codigo_ds160"))
        posicao = _acha(entradas, codigo)
        if posicao is None:
            raise HTTPException(status_code=404, detail="Código não encontrado neste processo")
        entradas[posicao].solicitante = dados.solicitante
        return tabela.atualizar(processo_id, {"codigo_ds160": monta_linhas(entradas)})

    @router.delete("/{processo_id}/codigos-ds160/{codigo}", response_model=modelo_out)
    def remove_codigo(processo_id: int, codigo: str):
        entradas = le_linhas(processo_ou_404(processo_id).get("codigo_ds160"))
        posicao = _acha(entradas, codigo)
        if posicao is None:
            raise HTTPException(status_code=404, detail="Código não encontrado neste processo")
        del entradas[posicao]
        return tabela.atualizar(processo_id, {"codigo_ds160": monta_linhas(entradas)})

    # ---------- notas: pedidos de alteração, texto livre ----------

    @router.post("/{processo_id}/notas-ds160", response_model=modelo_out, status_code=201)
    def adiciona_nota(processo_id: int, dados: NotaAdicionar):
        _recusa_linha_de_codigo(dados.texto)
        atual = processo_ou_404(processo_id).get("notas_ds160")
        nova = dados.texto if atual is None else f"{atual}\n{dados.texto}"
        return tabela.atualizar(processo_id, {"notas_ds160": nova})

    @router.patch("/{processo_id}/notas-ds160", response_model=modelo_out)
    def edita_nota(processo_id: int, dados: NotaEditar):
        _recusa_linha_de_codigo(dados.novo)
        atual = processo_ou_404(processo_id).get("notas_ds160") or ""
        ocorrencias = atual.count(dados.trecho)
        if ocorrencias == 0:
            raise HTTPException(status_code=404, detail="Trecho não encontrado na nota")
        if ocorrencias > 1:
            raise HTTPException(
                status_code=409,
                detail=f"O trecho aparece {ocorrencias} vezes na nota; informe um trecho mais específico",
            )
        nova = atual.replace(dados.trecho, dados.novo).strip()
        return tabela.atualizar(processo_id, {"notas_ds160": nova or None})

    @router.delete("/{processo_id}/notas-ds160", response_model=modelo_out)
    def limpa_nota(processo_id: int):
        processo_ou_404(processo_id)
        return tabela.atualizar(processo_id, {"notas_ds160": None})

    return router
