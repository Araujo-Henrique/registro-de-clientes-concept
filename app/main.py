from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Cliente(BaseModel):
    nome: str
    email: str
    telefone: str
    n_solicitantes: int
    data_casv: str
    data_entrevista: str
    consulado: str
    status_rascunho: str
    status_ds: str
    orientacao: str
    situacao: str
    resultado: str

class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    n_solicitantes: int | None = None
    data_casv: str | None = None
    data_entrevista: str | None = None
    consulado: str | None = None
    status_rascunho: str | None = None
    status_ds: str | None = None
    orientacao: str | None = None
    situacao: str | None = None
    resultado: str | None = None

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