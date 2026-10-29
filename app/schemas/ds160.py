import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, computed_field, field_validator

# AA00 + 6 caracteres = 10 no total
PADRAO_CODIGO = re.compile(r"^AA00[A-Z0-9]{6}$")
INICIO_CODIGO = re.compile(r"^AA00", re.IGNORECASE)

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _normaliza_codigo(codigo: str) -> str:
    codigo = codigo.strip().upper()
    if not PADRAO_CODIGO.match(codigo):
        raise ValueError("O código DS-160 começa com AA00 e tem 10 caracteres (AA00 + 6 letras/números)")
    return codigo


def _uma_linha(solicitante: str) -> str:
    if "\n" in solicitante or "\r" in solicitante:
        raise ValueError("O solicitante cabe em uma linha")
    return solicitante


class CodigoDS160(BaseModel):
    """Um formulário DS-160: o código e quem é o solicitante ('novo' quando o formulário foi refeito)."""
    model_config = ConfigDict(extra="forbid")

    codigo: str
    solicitante: Texto = Field(description="Primeiro nome do solicitante, ou 'novo'")

    @field_validator("codigo")
    @classmethod
    def _valida_codigo(cls, codigo):
        return _normaliza_codigo(codigo)

    _uma_linha = field_validator("solicitante")(_uma_linha)


class SolicitanteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    solicitante: Texto

    _uma_linha = field_validator("solicitante")(_uma_linha)


class CodigoDS160Out(BaseModel):
    codigo: str
    solicitante: str


class NotaAdicionar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: Texto


class NotaEditar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trecho: Texto
    novo: str  # vazio apaga o trecho


def linha_do_codigo(codigo: str, solicitante: str) -> str:
    return f"{codigo} - {solicitante}"


def le_linhas(texto: str | None) -> list[CodigoDS160Out]:
    """Lê a coluna codigo_ds160. Tolerante: o histórico pode ter linhas fora do padrão."""
    if not texto:
        return []
    entradas = []
    for linha in texto.splitlines():
        codigo, _, solicitante = linha.partition("-")
        entradas.append(CodigoDS160Out(codigo=codigo.strip(), solicitante=solicitante.strip()))
    return entradas


def monta_linhas(entradas: list[CodigoDS160Out]) -> str | None:
    if not entradas:
        return None
    return "\n".join(linha_do_codigo(e.codigo, e.solicitante) for e in entradas)


def tem_linha_de_codigo(texto: str) -> bool:
    return any(INICIO_CODIGO.match(linha.strip()) for linha in texto.splitlines())


class DS160Saida(BaseModel):
    """Parte da resposta de um processo que vem das colunas codigo_ds160 e notas_ds160."""
    # texto bruto do banco; a API expõe a lista estruturada em codigos_ds160
    codigo_ds160: str | None = Field(default=None, exclude=True)
    notas_ds160: str | None = None

    @computed_field
    @property
    def codigos_ds160(self) -> list[CodigoDS160Out]:
        return le_linhas(self.codigo_ds160)
