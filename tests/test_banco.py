import psycopg
import pytest

from app import db, store
from tests.conftest import payload_cliente, payload_obt


def test_atualizar_condicional_nao_grava_se_o_valor_mudou(cliente):
    processo = store.processos_obt.inserir(payload_obt(cliente["id"]))
    store.processos_obt.atualizar(processo["id"], {"notas_ds160": "primeira"})
    # quem leu a nota vazia (None) e tenta gravar depois que outra pessoa já escreveu
    assert store.processos_obt.atualizar(processo["id"], {"notas_ds160": "minha"}, se={"notas_ds160": None}) is None
    assert store.processos_obt.obter(processo["id"])["notas_ds160"] == "primeira"
    ok = store.processos_obt.atualizar(processo["id"], {"notas_ds160": "minha"}, se={"notas_ds160": "primeira"})
    assert ok["notas_ds160"] == "minha"


def test_edicao_simultanea_do_ds160_da_409(client, cliente, monkeypatch):
    criado = client.post("/processos-obt", json=payload_obt(cliente["id"])).json()
    leitura_antiga = store.processos_obt.obter(criado["id"])
    store.processos_obt.atualizar(criado["id"], {"notas_ds160": "escrita por outra pessoa"})
    # a rota leu o processo antes da outra pessoa gravar: simulamos devolvendo a leitura velha
    monkeypatch.setattr(store.processos_obt, "obter", lambda id: leitura_antiga)
    resposta = client.post(f"/processos-obt/{criado['id']}/notas-ds160", json={"texto": "minha nota"})
    assert resposta.status_code == 409
    monkeypatch.undo()
    assert store.processos_obt.obter(criado["id"])["notas_ds160"] == "escrita por outra pessoa"


def test_nome_duplicado_que_passa_pela_checagem_e_barrado_pelo_banco(client, monkeypatch):
    client.post("/clientes", json=payload_cliente())
    # duas requisições simultâneas passariam pela checagem; aqui a desligamos para o banco decidir
    monkeypatch.setattr(store, "achar_cliente_por_nome", lambda nome, ignorar_id=None: None)
    resposta = client.post("/clientes", json=payload_cliente(nome="ana souza"))
    assert resposta.status_code == 409
    assert len(client.get("/clientes").json()) == 1


def test_banco_fora_do_ar_da_503(client, monkeypatch):
    def cai(*args, **kwargs):
        raise psycopg.OperationalError("conexão recusada")
    monkeypatch.setattr(store.clientes, "listar", cai)
    assert client.get("/clientes").status_code == 503


def test_filtro_booleano_falso_nao_e_ignorado(client):
    inativos = client.get("/funcionarios", params={"ativo": False}).json()
    assert [f["nome"] for f in inativos] == ["Roger Cardoso", "Thiago Matos", "Esther Matos", "Joao Banks"]


def test_busca_por_nome_trata_percentual_como_texto_comum(client):
    client.post("/clientes", json=payload_cliente(nome="Ana Souza"))
    client.post("/clientes", json=payload_cliente(nome="Bia 100% Lima"))
    assert [c["nome"] for c in client.get("/clientes", params={"nome": "%"}).json()] == ["Bia 100% Lima"]
    assert [c["nome"] for c in client.get("/clientes", params={"nome": "SOUZA"}).json()] == ["Ana Souza"]


def test_dados_sao_gravados_de_verdade_no_banco(client):
    criado = client.post("/clientes", json=payload_cliente()).json()
    with db.conexao() as conn:
        linha = conn.execute("SELECT nome, telefone FROM clientes WHERE id = %s", [criado["id"]]).fetchone()
    assert linha == {"nome": "Ana Souza", "telefone": "41999999999"}


def test_data_despacho_vem_do_banco_igual_ao_calculado(client, cliente):
    from tests.conftest import payload_ren
    criado = client.post("/processos-ren", json=payload_ren(cliente["id"], data_casv="2026-10-16")).json()
    with db.conexao() as conn:
        no_banco = conn.execute("SELECT data_despacho FROM processos_ren WHERE id = %s", [criado["id"]]).fetchone()
    assert str(no_banco["data_despacho"]) == criado["data_despacho"] == "2026-10-09"


def test_guarda_recusa_banco_que_nao_termina_em_test(monkeypatch):
    # a mesma checagem do conftest, isolada: o nome do banco decide
    from psycopg.conninfo import conninfo_to_dict
    assert not conninfo_to_dict("postgresql://u@localhost/concept_client_registry")["dbname"].endswith("_test")
    assert conninfo_to_dict("postgresql://u@localhost/concept_client_registry_test")["dbname"].endswith("_test")
