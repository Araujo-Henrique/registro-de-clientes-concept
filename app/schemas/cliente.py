import re
from typing import Annotated

from pydantic import (BaseModel, ConfigDict, EmailStr, Field, StringConstraints,
                      field_validator, model_validator)

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def normaliza_nome(valor):
    # espaços repetidos viram um só e as pontas são aparadas (o banco exige nome sem espaço sobrando)
    if isinstance(valor, str):
        return re.sub(r"\s+", " ", valor).strip()
    return valor


def normaliza_telefone(valor):
    # Guarda só dígitos. Remove o 55 do Brasil apenas quando o tamanho confirma
    # que é código de país (12-13 dígitos), pois 55 também é um DDD (Santa Maria/RS).
    if valor is None:
        return valor
    digitos = re.sub(r"\D", "", str(valor))
    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]
    return digitos


class ClienteBase(BaseModel):
    """Forma de um cliente já gravado. email e telefone aceitam None porque o histórico não os tem."""
    model_config = ConfigDict(extra="forbid")

    nome: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, pattern=r"^\d{10,15}$")  # só dígitos; normalizado abaixo
    grupo: Texto | None = None  # grupo de WhatsApp quando o mesmo número atende vários clientes (agências, famílias)

    _normalizar_nome = field_validator("nome", mode="before")(normaliza_nome)
    _normalizar_telefone = field_validator("telefone", mode="before")(normaliza_telefone)


class ClienteCreate(ClienteBase):
    # cadastro novo exige e-mail e telefone
    email: EmailStr
    telefone: str = Field(pattern=r"^\d{10,15}$")


class ClienteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: Annotated[str, StringConstraints(min_length=1, max_length=200)] | None = None
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, pattern=r"^\d{10,15}$")
    grupo: Texto | None = None  # enviar null limpa o grupo

    _normalizar_nome = field_validator("nome", mode="before")(normaliza_nome)
    _normalizar_telefone = field_validator("telefone", mode="before")(normaliza_telefone)

    @model_validator(mode="after")
    def _obrigatorios_nao_podem_ser_nulos(self):
        for campo in ("nome", "email", "telefone"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"'{campo}' não pode ser removido")
        return self


class ClienteOut(BaseModel):
    id: int
    nome: str
    email: str | None
    telefone: str | None
    grupo: str | None
