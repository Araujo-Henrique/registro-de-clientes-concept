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

clientes = []
cliente_id = 1


@app.post("/clientes")
def cria_cliente(cliente: Cliente):
    global cliente_id

    novo_cliente = {
        "id": cliente_id,
        **cliente.model_dump()
    }

    clientes.append(novo_cliente)
    cliente_id +=1

    return novo_cliente

@app.get("/clientes")
def busca_clientes():
    return clientes

@app.get("/clientes/{cliente_id}")
def busca_cliente_por_id(cliente_id: int):
    for cliente in clientes:
        if cliente["id"] == cliente_id:
            return cliente

    raise HTTPException(
        status_code=404,
        detail="Cliente não encontrado"
    )

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