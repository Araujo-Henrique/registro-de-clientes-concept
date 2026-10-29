from pydantic import BaseModel


class FuncionarioOut(BaseModel):
    id: int
    nome: str
    ativo: bool
