import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture(autouse=True)
def banco_limpo():
    # cada teste começa com as tabelas vazias (e os funcionários recriados)
    store.reiniciar()


@pytest.fixture
def client():
    return TestClient(app)


def payload_cliente(**extra):
    return {"nome": "Ana Souza", "email": "ana@example.com", "telefone": "41999999999", **extra}


def payload_obt(cliente_id, **extra):
    return {
        "cliente_id": cliente_id, "consulado": "POA", "n_solicitantes": 2,
        "status_rascunho": "Enviado", "status_ds": "Fechado", "orientacao": "Fornecidas",
        "situacao": "Processando", "resultado": "Processando", **extra,
    }


def payload_ren(cliente_id, **extra):
    return {
        "cliente_id": cliente_id, "consulado": "SP", "n_solicitantes": 1,
        "docs": "Entregue", "status_rascunho": "Enviado", "status_ds": "Fechado",
        "situacao": "Processando", **extra,
    }


@pytest.fixture
def cliente(client):
    resposta = client.post("/clientes", json=payload_cliente())
    assert resposta.status_code == 201
    return resposta.json()
