import os
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict

from app import db
from app.main import app

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS_DO_SCHEMA = ["db/01_schema.sql", "db/02_processos_ren.sql"]

FUNCIONARIOS = [
    ("Gabriel Vieira", True),
    ("Marcio Conde", True),
    ("Henrique Araujo", True),
    ("Roger Cardoso", False),
    ("Thiago Matos", False),
    ("Esther Matos", False),
    ("Joao Banks", False),
]


@pytest.fixture(scope="session", autouse=True)
def banco_de_teste():
    """Recria o schema num banco SÓ de testes e abre o pool nele.

    Os testes apagam tudo, então a guarda abaixo recusa qualquer banco cujo nome não termine em _test:
    assim é impossível rodar isto por engano contra o banco real.
    """
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.exit("Defina TEST_DATABASE_URL apontando para um banco de teste (ex.: .../concept_client_registry_test)")
    nome = conninfo_to_dict(url).get("dbname", "")
    if not nome.endswith("_test"):
        pytest.exit(f"Recusado: o banco de teste precisa terminar em _test (recebido: '{nome}')")

    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
        for script in SCRIPTS_DO_SCHEMA:
            conn.execute((RAIZ / script).read_text(encoding="utf-8"))
    db.abrir(url)
    yield
    db.fechar()


@pytest.fixture(autouse=True)
def banco_limpo(banco_de_teste):
    # cada teste começa com as tabelas vazias (ids reiniciados) e os funcionários recriados
    with db.conexao() as conn:
        conn.execute("TRUNCATE processos_obt, processos_ren, passaportes, clientes, funcionarios "
                     "RESTART IDENTITY CASCADE")
        with conn.cursor() as cursor:
            cursor.executemany("INSERT INTO funcionarios (nome, ativo) VALUES (%s, %s)", FUNCIONARIOS)


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
