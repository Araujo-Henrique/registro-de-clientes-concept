from tests.conftest import payload_cliente, payload_obt


def test_cria_e_busca_cliente(client):
    criado = client.post("/clientes", json=payload_cliente())
    assert criado.status_code == 201
    corpo = criado.json()
    assert corpo["id"] == 1 and corpo["nome"] == "Ana Souza"

    assert client.get("/clientes/1").json() == corpo
    assert client.get("/clientes").json() == [corpo]


def test_telefone_e_normalizado_sem_o_55_do_brasil(client):
    resposta = client.post("/clientes", json=payload_cliente(telefone="+55 (41) 99999-9999"))
    assert resposta.json()["telefone"] == "41999999999"


def test_telefone_com_ddd_55_de_10_digitos_nao_perde_o_55(client):
    resposta = client.post("/clientes", json=payload_cliente(telefone="55 3333-4444"))
    assert resposta.json()["telefone"] == "5533334444"


def test_email_e_telefone_sao_obrigatorios_no_cadastro(client):
    assert client.post("/clientes", json={"nome": "Sem Contato"}).status_code == 422


def test_email_invalido(client):
    assert client.post("/clientes", json=payload_cliente(email="não-é-email")).status_code == 422


def test_campo_desconhecido_e_recusado(client):
    assert client.post("/clientes", json=payload_cliente(cor_favorita="azul")).status_code == 422


def test_nome_duplicado_ignora_maiuscula_e_espacos(client, cliente):
    resposta = client.post("/clientes", json=payload_cliente(nome="  ANA   souza "))
    assert resposta.status_code == 409


def test_telefone_repetido_e_permitido(client, cliente):
    resposta = client.post("/clientes", json=payload_cliente(nome="Bia Souza"))
    assert resposta.status_code == 201


def test_cliente_inexistente_da_404(client):
    assert client.get("/clientes/99").status_code == 404
    assert client.patch("/clientes/99", json={"grupo": "x"}).status_code == 404
    assert client.delete("/clientes/99").status_code == 404


def test_patch_altera_so_o_enviado(client, cliente):
    resposta = client.patch(f"/clientes/{cliente['id']}", json={"grupo": "Agência X"})
    assert resposta.status_code == 200
    assert resposta.json()["grupo"] == "Agência X"
    assert resposta.json()["email"] == "ana@example.com"


def test_patch_null_limpa_o_grupo(client, cliente):
    client.patch(f"/clientes/{cliente['id']}", json={"grupo": "Agência X"})
    resposta = client.patch(f"/clientes/{cliente['id']}", json={"grupo": None})
    assert resposta.json()["grupo"] is None


def test_patch_nao_deixa_remover_email(client, cliente):
    assert client.patch(f"/clientes/{cliente['id']}", json={"email": None}).status_code == 422


def test_patch_para_nome_de_outro_cliente_da_409(client, cliente):
    outro = client.post("/clientes", json=payload_cliente(nome="Bia Souza")).json()
    assert client.patch(f"/clientes/{outro['id']}", json={"nome": "ana souza"}).status_code == 409


def test_patch_com_o_proprio_nome_nao_conflita(client, cliente):
    resposta = client.patch(f"/clientes/{cliente['id']}", json={"nome": "ANA SOUZA"})
    assert resposta.status_code == 200 and resposta.json()["nome"] == "ANA SOUZA"


def test_filtros_e_paginacao(client):
    for nome in ("Ana", "Bruno", "Carla"):
        client.post("/clientes", json=payload_cliente(nome=nome))
    assert [c["nome"] for c in client.get("/clientes", params={"nome": "ru"}).json()] == ["Bruno"]
    assert [c["nome"] for c in client.get("/clientes", params={"limit": 1, "offset": 1}).json()] == ["Bruno"]


def test_apagar_cliente_com_processo_vinculado_da_409(client, cliente):
    client.post("/processos-obt", json=payload_obt(cliente["id"]))
    resposta = client.delete(f"/clientes/{cliente['id']}")
    assert resposta.status_code == 409
    assert resposta.json()["detail"]["vinculos"] == {"processos de obtenção": 1}
    assert client.get(f"/clientes/{cliente['id']}").status_code == 200


def test_apagar_cliente_sem_vinculos(client, cliente):
    assert client.delete(f"/clientes/{cliente['id']}").status_code == 200
    assert client.get(f"/clientes/{cliente['id']}").status_code == 404
