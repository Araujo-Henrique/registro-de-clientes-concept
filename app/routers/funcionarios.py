from fastapi import APIRouter

from app import store
from app.routers.comum import igual, obter_ou_404
from app.schemas.funcionario import FuncionarioOut

router = APIRouter(prefix="/funcionarios", tags=["Funcionários"])


@router.get("", response_model=list[FuncionarioOut])
def busca_funcionarios(ativo: bool | None = None):
    return store.funcionarios.listar(igual(ativo=ativo))


@router.get("/{funcionario_id}", response_model=FuncionarioOut)
def busca_funcionario(funcionario_id: int):
    return obter_ou_404(store.funcionarios, funcionario_id, "Funcionário")
