from datetime import date, timedelta
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, computed_field

from app.enums import Consulado, DocsREN, Rascunho, SituacaoREN, StatusDS
from app.schemas.ds160 import DS160Saida

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ProcessoRENBase(BaseModel):
    # extra="forbid": mandar data_despacho (campo calculado) dá erro 422 em vez de ser ignorado
    model_config = ConfigDict(extra="forbid")

    cliente_id: int

    consulado: Consulado
    n_solicitantes: int = Field(gt=0)
    data_casv: date | None = None  # Padrão AAAA-MM-DD

    docs: DocsREN
    status_rascunho: Rascunho
    status_ds: StatusDS
    situacao: SituacaoREN

    codigo_rastreio: Texto | None = None  # só surge no fim do processo
    endereco: Texto | None = None  # endereço cadastrado quando o cliente já pagou a taxa do sedex


class ProcessoRENCreate(ProcessoRENBase):
    pass


class ProcessoRENUpdate(BaseModel):
    """Todos os campos opcionais. cliente_id não muda depois de criado."""
    model_config = ConfigDict(extra="forbid")

    consulado: Consulado | None = None
    n_solicitantes: int | None = Field(default=None, gt=0)
    data_casv: date | None = None

    docs: DocsREN | None = None
    status_rascunho: Rascunho | None = None
    status_ds: StatusDS | None = None
    situacao: SituacaoREN | None = None

    codigo_rastreio: Texto | None = None
    endereco: Texto | None = None


class ProcessoRENOut(ProcessoRENBase, DS160Saida):
    id: int

    @computed_field
    @property
    def data_despacho(self) -> date | None:
        # sempre 7 dias antes do CASV; no banco será coluna gerada (casv - 7)
        if self.data_casv is None:
            return None
        return self.data_casv - timedelta(days=7)
