from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from enum import Enum

app = FastAPI()

class Consulado(str, Enum):
    POA = "POA"
    RJ = "RJ"
    BSB = "BSB"
    SP = "SP"
    REC = "REC"

class Rascunho(str, Enum):
    PENDENTE = "Pendente"
    PARCIAL = "Parcial"
    ENVIADO = "Enviado"

class StatusDS(str, Enum):
    PENDENTE = "Pendente"
    PARCIAL = "Parcial"
    ABERTO = "Aberto"
    PREENCHIDO = "Preenchido"
    FECHADO = "Fechado"

class Situacao(str, Enum):
    PAG_PENDENTE = "Pagamento Pendente"
    BOLETO = "Boleto"
    CREDITO =  "Credito"
    LIMBO = "Limbo"
    PROCESSANDO = "Processando"
    CADASTRO = "Cadastro"
    ADMINISTRATIVO = "Administrativo"
    CONCLUIDO = "Concluido"

class Resultado(str, Enum):
    PROCESSANDO = "Processando"
    APROVADO = "Aprovado"
    NEGADO = "Negado"


class Orientacao(str, Enum):
    OPTA = "Opt A"
    FORNECIDAS = "Fornecidas"
    AGENDADA = "Agendada"

class Cliente(BaseModel):
    nome: str
    email: EmailStr
    telefone: str = Field(pattern=r"^\d{10,11}$") # Telefone precisa ter DDD e somente os números. Sem traço ou espaço
    n_solicitantes: int = Field(gt=0)

    data_casv: date | None = None #Padrão AAAA-MM-DD
    data_entrevista: date | None = None #Padrão AAAA-MM-DD

    consulado: Consulado
    status_rascunho: Rascunho
    status_ds: StatusDS

    orientacao: Orientacao
    orientacao_data: date | None = None #Padrão AAAA-MM-DD
    
    situacao: Situacao
    resultado: Resultado

class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None

    telefone: str | None = Field(
        default=None,
        pattern=r"^\d{10,11}$"
    )

    n_solicitantes: int | None = Field(
        default=None,
        gt=0
    )

    data_casv: date | None = None
    data_entrevista: date | None = None

    consulado: Consulado | None = None
    status_rascunho: Rascunho | None = None
    status_ds: StatusDS | None = None

    orientacao: Orientacao | None = None
    orientacao_data: date | None = None

    situacao: Situacao | None = None
    resultado: Resultado | None = None

clientes = []
cliente_id = 1

#Cria novos clientes
@app.post("/clientes")
def cria_cliente(cliente: Cliente):
    global cliente_id

    novo_cliente = {
        "id": cliente_id,
        **cliente.model_dump()
    }

    clientes.append(novo_cliente)
    cliente_id += 1

    return novo_cliente

#Busca lista de clientes registrados
@app.get("/clientes")
def busca_clientes():
    return clientes

#Busca um cliente específico
@app.get("/clientes/{cliente_id}")
def busca_cliente_por_id(cliente_id: int):
    for cliente in clientes:
        if cliente["id"] == cliente_id:
            return cliente

    raise HTTPException(
        status_code=404,
        detail="Cliente não encontrado"
    )

#Deleta um cliente específico
@app.delete("/clientes/{cliente_id}")
def deleta_cliente_por_id(cliente_id: int):
    for index, cliente in enumerate(clientes):
        if cliente["id"] == cliente_id:
            cliente_removido = clientes.pop(index)
            return cliente_removido

    raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

#Atualiza os dados de um cliente específico
@app.patch("/clientes/{cliente_id}")
def atualizar_cliente(cliente_id: int, dados: ClienteUpdate):

    for cliente in clientes:
        if cliente["id"] == cliente_id:
            dados_atualizados = dados.model_dump(exclude_unset=True)

            for campo, valor in dados_atualizados.items():
                cliente[campo] = valor

            return cliente

    raise HTTPException(
        status_code=404,
        detail="Cliente não encontrado"
    )