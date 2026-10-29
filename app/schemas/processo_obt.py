from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

from app.enums import (ConsuladoOBT, Monitoramento, Orientacao, Resultado, Rascunho,
                       SituacaoOBT, StatusDS)
from app.schemas.ds160 import DS160Saida

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _rejeita_nd(valor):
    if valor == ConsuladoOBT.ND:
        raise ValueError("'N/D' existe só no histórico; informe o consulado")
    return valor


class ProcessoOBTBase(BaseModel):
    """Forma de um processo de obtenção já gravado (aceita consulado N/D do histórico)."""
    model_config = ConfigDict(extra="forbid")

    cliente_id: int

    consulado: ConsuladoOBT
    n_solicitantes: int = Field(gt=0)
    monitoramento: Monitoramento = Monitoramento.ATIVO

    data_casv: date | None = None  # Padrão AAAA-MM-DD
    data_entrevista: date | None = None
    data_vencimento_taxa: date | None = None

    status_rascunho: Rascunho
    status_ds: StatusDS

    orientacao: Orientacao
    orientacao_data: date | None = None
    orientacao_por_id: int | None = None  # id de /funcionarios

    situacao: SituacaoOBT
    codigo_rastreio: Texto | None = None
    resultado: Resultado

    @model_validator(mode="after")
    def _agendada_exige_data(self):
        if self.orientacao == Orientacao.AGENDADA and self.orientacao_data is None:
            raise ValueError(
                "Se o status da orientação está como 'agendada' é obrigatório ter uma data definida"
            )
        return self


class ProcessoOBTCreate(ProcessoOBTBase):
    _sem_nd = field_validator("consulado")(_rejeita_nd)


class ProcessoOBTUpdate(BaseModel):
    """Todos os campos opcionais. cliente_id não muda depois de criado."""
    model_config = ConfigDict(extra="forbid")

    consulado: ConsuladoOBT | None = None
    n_solicitantes: int | None = Field(default=None, gt=0)
    monitoramento: Monitoramento | None = None

    data_casv: date | None = None
    data_entrevista: date | None = None
    data_vencimento_taxa: date | None = None

    status_rascunho: Rascunho | None = None
    status_ds: StatusDS | None = None

    orientacao: Orientacao | None = None
    orientacao_data: date | None = None
    orientacao_por_id: int | None = None

    situacao: SituacaoOBT | None = None
    codigo_rastreio: Texto | None = None
    resultado: Resultado | None = None

    _sem_nd = field_validator("consulado")(_rejeita_nd)


class ProcessoOBTOut(ProcessoOBTBase, DS160Saida):
    id: int
