from app import store
from tests.conftest import payload_obt


def test_cria_processo_obt(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(cliente["id"]))
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] == 1 and corpo["monitoramento"] == "Ativo"
    assert corpo["codigo_rastreio"] is None


def test_cliente_inexistente_da_404(client):
    assert client.post("/processos-obt", json=payload_obt(99)).status_code == 404


def test_funcionario_inexistente_da_404(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(cliente["id"], orientacao_por_id=99))
    assert resposta.status_code == 404


def test_orientacao_por_funcionario_existente(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(cliente["id"], orientacao_por_id=1))
    assert resposta.status_code == 201 and resposta.json()["orientacao_por_id"] == 1


def test_agendada_sem_data_e_recusada(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(cliente["id"], orientacao="Agendada"))
    assert resposta.status_code == 422


def test_agendada_com_data(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(
        cliente["id"], orientacao="Agendada", orientacao_data="2026-11-10"))
    assert resposta.status_code == 201


def test_patch_para_agendada_olha_a_data_ja_gravada(client, cliente):
    # cliente cadastrado com data mas sem Agendada: o PATCH precisa enxergar a data atual
    criado = client.post("/processos-obt", json=payload_obt(
        cliente["id"], orientacao="Fornecidas", orientacao_data="2026-11-10")).json()
    resposta = client.patch(f"/processos-obt/{criado['id']}", json={"orientacao": "Agendada"})
    assert resposta.status_code == 200


def test_patch_para_agendada_sem_data_da_422(client, cliente):
    criado = client.post("/processos-obt", json=payload_obt(cliente["id"])).json()
    resposta = client.patch(f"/processos-obt/{criado['id']}", json={"orientacao": "Agendada"})
    assert resposta.status_code == 422


def test_patch_null_limpa_data_opcional(client, cliente):
    criado = client.post("/processos-obt", json=payload_obt(cliente["id"], data_casv="2026-10-10")).json()
    resposta = client.patch(f"/processos-obt/{criado['id']}", json={"data_casv": None})
    assert resposta.status_code == 200 and resposta.json()["data_casv"] is None


def test_patch_null_em_campo_obrigatorio_da_422(client, cliente):
    criado = client.post("/processos-obt", json=payload_obt(cliente["id"])).json()
    assert client.patch(f"/processos-obt/{criado['id']}", json={"status_ds": None}).status_code == 422


def test_cliente_id_nao_pode_ser_alterado(client, cliente):
    criado = client.post("/processos-obt", json=payload_obt(cliente["id"])).json()
    assert client.patch(f"/processos-obt/{criado['id']}", json={"cliente_id": 2}).status_code == 422


def test_situacao_pago_e_codigo_de_rastreio(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(
        cliente["id"], situacao="Pago", codigo_rastreio="/AA12345678BR"))
    assert resposta.status_code == 201 and resposta.json()["codigo_rastreio"] == "/AA12345678BR"


def test_codigo_de_rastreio_vazio_e_recusado(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(cliente["id"], codigo_rastreio="  "))
    assert resposta.status_code == 422


def test_situacao_entrevista_nao_existe_no_obt(client, cliente):
    assert client.post("/processos-obt", json=payload_obt(cliente["id"], situacao="Entrevista")).status_code == 422


def test_cadastro_novo_nao_aceita_consulado_nd(client, cliente):
    assert client.post("/processos-obt", json=payload_obt(cliente["id"], consulado="N/D")).status_code == 422


def test_historico_com_nd_pode_ser_lido_e_editado(client, cliente):
    linha = store.processos_obt.inserir({
        **payload_obt(cliente["id"]), "consulado": "N/D", "monitoramento": "Concluido",
        "data_casv": None, "data_entrevista": None, "data_vencimento_taxa": None,
        "orientacao_data": None, "orientacao_por_id": None, "codigo_rastreio": None,
    })
    assert client.get(f"/processos-obt/{linha['id']}").json()["consulado"] == "N/D"
    # editar outro campo não pode ser barrado pelo N/D que já estava gravado
    assert client.patch(f"/processos-obt/{linha['id']}", json={"situacao": "Concluido"}).status_code == 200
    # mas escolher N/D numa edição é recusado
    assert client.patch(f"/processos-obt/{linha['id']}", json={"consulado": "N/D"}).status_code == 422


def test_filtros(client, cliente):
    client.post("/processos-obt", json=payload_obt(cliente["id"], situacao="Pago"))
    client.post("/processos-obt", json=payload_obt(cliente["id"], consulado="SP"))
    assert len(client.get("/processos-obt", params={"situacao": "Pago"}).json()) == 1
    assert len(client.get("/processos-obt", params={"consulado": "SP"}).json()) == 1
    assert len(client.get("/processos-obt", params={"cliente_id": cliente["id"]}).json()) == 2
    assert client.get("/processos-obt", params={"situacao": "Inventada"}).status_code == 422


def test_delete_e_404(client, cliente):
    criado = client.post("/processos-obt", json=payload_obt(cliente["id"])).json()
    assert client.delete(f"/processos-obt/{criado['id']}").status_code == 200
    assert client.get(f"/processos-obt/{criado['id']}").status_code == 404
