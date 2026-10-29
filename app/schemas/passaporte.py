from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.enums import SituacaoPassaporte


class PassaporteBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cliente_id: int
    n_solicitantes: int = Field(gt=0)
    data_pf: date | None = None  # Padrão AAAA-MM-DD
    prazo_pf: date | None = None
    situacao: SituacaoPassaporte | None = None


class PassaporteCreate(PassaporteBase):
    pass


class PassaporteUpdate(BaseModel):
    """Todos os campos opcionais. cliente_id não muda depois de criado."""
    model_config = ConfigDict(extra="forbid")

    n_solicitantes: int | None = Field(default=None, gt=0)
    data_pf: date | None = None
    prazo_pf: date | None = None
    situacao: SituacaoPassaporte | None = None


class PassaporteOut(PassaporteBase):
    id: int
