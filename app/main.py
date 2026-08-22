from fastapi import FastAPI
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


@app.post("/clientes")
def create_client(cliente: Cliente):
    clientes.append(cliente)
    return cliente

@app.get("/clientes")
def get_client():
    return clientes