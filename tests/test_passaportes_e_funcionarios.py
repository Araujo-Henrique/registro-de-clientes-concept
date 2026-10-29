def payload_passaporte(cliente_id, **extra):
    return {"cliente_id": cliente_id, "n_solicitantes": 2, **extra}


def test_cria_passaporte_sem_situacao(client, cliente):
    resposta = client.post("/passaportes", json=payload_passaporte(cliente["id"]))
    assert resposta.status_code == 201
    assert resposta.json()["situacao"] is None and resposta.json()["data_pf"] is None


def test_cria_passaporte_completo(client, cliente):
    resposta = client.post("/passaportes", json=payload_passaporte(
        cliente["id"], data_pf="2026-10-01", prazo_pf="2026-10-09", situacao="Pix"))
    assert resposta.status_code == 201 and resposta.json()["situacao"] == "Pix"


def test_cliente_inexistente_da_404(client):
    assert client.post("/passaportes", json=payload_passaporte(99)).status_code == 404


def test_situacao_invalida(client, cliente):
    assert client.post("/passaportes", json=payload_passaporte(cliente["id"], situacao="Safado")).status_code == 422


def test_n_solicitantes_precisa_ser_positivo(client, cliente):
    assert client.post("/passaportes", json=payload_passaporte(cliente["id"], n_solicitantes=0)).status_code == 422


def test_patch_e_limpar_situacao(client, cliente):
    criado = client.post("/passaportes", json=payload_passaporte(cliente["id"], situacao="Pago")).json()
    assert client.patch(f"/passaportes/{criado['id']}", json={"situacao": "Concluido"}).json()["situacao"] == "Concluido"
    assert client.patch(f"/passaportes/{criado['id']}", json={"situacao": None}).json()["situacao"] is None


def test_filtro_por_cliente_e_situacao(client, cliente):
    client.post("/passaportes", json=payload_passaporte(cliente["id"], situacao="Pago"))
    client.post("/passaportes", json=payload_passaporte(cliente["id"]))
    assert len(client.get("/passaportes", params={"situacao": "Pago"}).json()) == 1
    assert len(client.get("/passaportes", params={"cliente_id": cliente["id"]}).json()) == 2


def test_apagar_cliente_com_passaporte_da_409(client, cliente):
    criado = client.post("/passaportes", json=payload_passaporte(cliente["id"])).json()
    assert client.delete(f"/clientes/{cliente['id']}").status_code == 409
    assert client.delete(f"/passaportes/{criado['id']}").status_code == 200
    assert client.delete(f"/clientes/{cliente['id']}").status_code == 200


def test_funcionarios_listados_com_ativos_e_inativos(client):
    todos = client.get("/funcionarios").json()
    assert len(todos) == 7
    ativos = client.get("/funcionarios", params={"ativo": True}).json()
    assert [f["nome"] for f in ativos] == ["Gabriel Vieira", "Marcio Conde", "Henrique Araujo"]
    assert client.get("/funcionarios/99").status_code == 404
