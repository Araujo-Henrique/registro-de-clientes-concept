from tests.conftest import payload_ren


def test_data_despacho_e_calculada_7_dias_antes_do_casv(client, cliente):
    resposta = client.post("/processos-ren", json=payload_ren(cliente["id"], data_casv="2026-10-16"))
    assert resposta.status_code == 201
    assert resposta.json()["data_despacho"] == "2026-10-09"


def test_sem_casv_nao_ha_despacho(client, cliente):
    resposta = client.post("/processos-ren", json=payload_ren(cliente["id"]))
    assert resposta.json()["data_despacho"] is None


def test_data_despacho_nao_pode_ser_enviada(client, cliente):
    resposta = client.post("/processos-ren", json=payload_ren(
        cliente["id"], data_casv="2026-10-16", data_despacho="2026-10-01"))
    assert resposta.status_code == 422
    resposta = client.post("/processos-ren", json=payload_ren(cliente["id"], data_casv="2026-10-16"))
    assert client.patch(f"/processos-ren/{resposta.json()['id']}",
                        json={"data_despacho": "2026-10-01"}).status_code == 422


def test_despacho_acompanha_a_mudanca_do_casv(client, cliente):
    criado = client.post("/processos-ren", json=payload_ren(cliente["id"], data_casv="2026-10-16")).json()
    resposta = client.patch(f"/processos-ren/{criado['id']}", json={"data_casv": "2026-11-20"})
    assert resposta.json()["data_despacho"] == "2026-11-13"
    resposta = client.patch(f"/processos-ren/{criado['id']}", json={"data_casv": None})
    assert resposta.json()["data_despacho"] is None


def test_despacho_cruza_a_virada_do_mes(client, cliente):
    resposta = client.post("/processos-ren", json=payload_ren(cliente["id"], data_casv="2026-03-03"))
    assert resposta.json()["data_despacho"] == "2026-02-24"


def test_cliente_inexistente_da_404(client):
    assert client.post("/processos-ren", json=payload_ren(99)).status_code == 404


def test_situacao_entrevista_existe_no_ren_e_pago_nao(client, cliente):
    assert client.post("/processos-ren", json=payload_ren(cliente["id"], situacao="Entrevista")).status_code == 201
    assert client.post("/processos-ren", json=payload_ren(cliente["id"], situacao="Pago")).status_code == 422


def test_docs_parcial_e_valido_e_valor_estranho_nao(client, cliente):
    assert client.post("/processos-ren", json=payload_ren(cliente["id"], docs="Parcial")).status_code == 201
    assert client.post("/processos-ren", json=payload_ren(cliente["id"], docs="Solicitado")).status_code == 422


def test_rastreio_e_endereco_opcionais_mas_nao_vazios(client, cliente):
    ok = client.post("/processos-ren", json=payload_ren(
        cliente["id"], codigo_rastreio="/AA22222", endereco="Rua A, 10, Curitiba"))
    assert ok.status_code == 201
    assert client.post("/processos-ren", json=payload_ren(cliente["id"], endereco="")).status_code == 422
    assert client.post("/processos-ren", json=payload_ren(cliente["id"], codigo_rastreio=" ")).status_code == 422


def test_ren_nao_tem_monitoramento_nem_resultado(client, cliente):
    resposta = client.post("/processos-ren", json=payload_ren(cliente["id"], monitoramento="Ativo"))
    assert resposta.status_code == 422


def test_apagar_cliente_com_ren_da_409(client, cliente):
    client.post("/processos-ren", json=payload_ren(cliente["id"]))
    resposta = client.delete(f"/clientes/{cliente['id']}")
    assert resposta.status_code == 409
    assert resposta.json()["detail"]["vinculos"] == {"processos de renovação": 1}


def test_filtros_e_delete(client, cliente):
    a = client.post("/processos-ren", json=payload_ren(cliente["id"], consulado="POA")).json()
    client.post("/processos-ren", json=payload_ren(cliente["id"], consulado="SP"))
    assert len(client.get("/processos-ren", params={"consulado": "POA"}).json()) == 1
    assert client.delete(f"/processos-ren/{a['id']}").status_code == 200
    assert client.get(f"/processos-ren/{a['id']}").status_code == 404
