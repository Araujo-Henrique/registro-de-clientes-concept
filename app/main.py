from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import date
from enum import Enum
import re

app = FastAPI()

class Consulado(str, Enum):
    POA = "POA"
    RIO = "RIO"
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
    REVISADO = "Revisado"
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


class Monitoramento(str, Enum):
    ATIVO = "Ativo"
    CONCLUIDO = "Concluido"


def normaliza_telefone(valor):
    # Guarda só dígitos. Remove o 55 do Brasil apenas quando o tamanho confirma
    # que é código de país (12-13 dígitos), pois 55 também é um DDD (Santa Maria/RS).
    if valor is None:
        return valor
    digitos = re.sub(r"\D", "", str(valor))
    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]
    return digitos


def orientacao_exige_data(orientacao, orientacao_data) -> bool:
    return orientacao == Orientacao.AGENDADA and orientacao_data is None

def _validar_orientacao_data(self):
    if orientacao_exige_data(self.orientacao, self.orientacao_data):
        raise ValueError(
            "Se o status da orientação está como 'agendada' é obrigatório ter uma data definida"
        )
    return self


class Cliente(BaseModel):
    nome: str
    email: EmailStr
    telefone: str = Field(pattern=r"^\d{10,15}$") # Só dígitos (10-11 nacional, até 15 internacional). Normalizado pelo validator abaixo
    grupo: str | None = None # Nome do grupo de WhatsApp quando o mesmo número atende vários clientes (agências, famílias)
    n_solicitantes: int = Field(gt=0)

    monitoramento: Monitoramento = Monitoramento.ATIVO

    data_casv: date | None = None #Padrão AAAA-MM-DD
    data_entrevista: date | None = None #Padrão AAAA-MM-DD
    data_vencimento_taxa: date | None = None #Padrão AAAA-MM-DD

    consulado: Consulado
    status_rascunho: Rascunho
    status_ds: StatusDS

    orientacao: Orientacao
    orientacao_data: date | None = None #Padrão AAAA-MM-DD
    orientacao_por: str | None = Field(default=None, min_length=1, max_length=50) # Nome (e sobrenome, se preciso) de quem forneceu

    situacao: Situacao
    resultado: Resultado

    _normalizar_telefone = field_validator("telefone", mode="before")(normaliza_telefone)
    _checar_orientacao = model_validator(mode="after")(_validar_orientacao_data)

class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None

    telefone: str | None = Field(
        default=None,
        pattern=r"^\d{10,15}$"
    )
    grupo: str | None = None

    n_solicitantes: int | None = Field(
        default=None,
        gt=0
    )

    monitoramento: Monitoramento | None = None

    data_casv: date | None = None
    data_entrevista: date | None = None
    data_vencimento_taxa: date | None = None

    consulado: Consulado | None = None
    status_rascunho: Rascunho | None = None
    status_ds: StatusDS | None = None

    orientacao: Orientacao | None = None
    orientacao_data: date | None = None
    orientacao_por: str | None = Field(default=None, min_length=1, max_length=50)

    situacao: Situacao | None = None
    resultado: Resultado | None = None

    _normalizar_telefone = field_validator("telefone", mode="before")(normaliza_telefone)

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
            dados_atualizados = dados.model_dump(
                exclude_unset=True,
                exclude_none=True
                )

            cliente_final = {**cliente, **dados_atualizados}
            if orientacao_exige_data(cliente_final["orientacao"],
                                     cliente_final["orientacao_data"]):
                raise HTTPException(
                    status_code=422,
                    detail="Se o status da orientação está como 'agendada' é obrigatório ter uma data definida"
                )


            for campo, valor in dados_atualizados.items():
                cliente[campo] = valor

            return cliente

    raise HTTPException(
        status_code=404,
        detail="Cliente não encontrado"
    )