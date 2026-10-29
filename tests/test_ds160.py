import pytest

from app import store
from tests.conftest import payload_obt, payload_ren

TIPOS = [("processos-obt", payload_obt), ("processos-ren", payload_ren)]


@pytest.fixture(params=TIPOS, ids=["obt", "ren"])
def processo(request, client, cliente):
    rota, payload = request.param
    criado = client.post(f"/{rota}", json=payload(cliente["id"])).json()
    return f"/{rota}/{criado['id']}"


def adiciona(client, processo, codigo, solicitante):
    return client.post(f"{processo}/codigos-ds160", json={"codigo": codigo, "solicitante": solicitante})


def test_processo_novo_nao_tem_codigo_nem_nota(client, processo):
    corpo = client.get(processo).json()
    assert corpo["codigos_ds160"] == [] and corpo["notas_ds160"] is None
    assert "codigo_ds160" not in corpo  # o texto bruto não vaza para a API


def test_adiciona_codigos_de_varios_solicitantes(client, processo):
    assert adiciona(client, processo, "AA00000001", "Maria").status_code == 201
    resposta = adiciona(client, processo, "aa00bcd123", "novo")  # minúsculas são normalizadas
    assert resposta.json()["codigos_ds160"] == [
        {"codigo": "AA00000001", "solicitante": "Maria"},
        {"codigo": "AA00BCD123", "solicitante": "novo"},
    ]


@pytest.mark.parametrize("codigo", ["AA0000001", "AA000000001", "BB00000001", "AA01000001", "AA00-00001", ""])
def test_codigo_fora_do_padrao_da_422(client, processo, codigo):
    assert adiciona(client, processo, codigo, "Maria").status_code == 422


def test_solicitante_obrigatorio_e_em_uma_linha(client, processo):
    assert adiciona(client, processo, "AA00000001", "  ").status_code == 422
    assert adiciona(client, processo, "AA00000001", "Maria\nAA00000002").status_code == 422


def test_codigo_repetido_no_mesmo_processo_da_409(client, processo):
    adiciona(client, processo, "AA00000001", "Maria")
    assert adiciona(client, processo, "AA00000001", "Outra").status_code == 409


def test_edita_so_o_solicitante_do_codigo_indicado(client, processo):
    adiciona(client, processo, "AA00000001", "Maria")
    adiciona(client, processo, "AA00000002", "novo")
    resposta = client.patch(f"{processo}/codigos-ds160/AA00000002", json={"solicitante": "Joao"})
    assert resposta.json()["codigos_ds160"] == [
        {"codigo": "AA00000001", "solicitante": "Maria"},
        {"codigo": "AA00000002", "solicitante": "Joao"},
    ]
    assert client.patch(f"{processo}/codigos-ds160/AA00999999", json={"solicitante": "X"}).status_code == 404


def test_remove_codigo_e_ultimo_deixa_vazio(client, processo):
    adiciona(client, processo, "AA00000001", "Maria")
    adiciona(client, processo, "AA00000002", "novo")
    resposta = client.delete(f"{processo}/codigos-ds160/AA00000001")
    assert [c["codigo"] for c in resposta.json()["codigos_ds160"]] == ["AA00000002"]
    resposta = client.delete(f"{processo}/codigos-ds160/AA00000002")
    assert resposta.json()["codigos_ds160"] == []
    assert client.delete(f"{processo}/codigos-ds160/AA00000002").status_code == 404


def test_historico_fora_do_padrao_e_lido_sem_quebrar(client, cliente):
    linha = store.processos_obt.inserir({**payload_obt(cliente["id"]),
                                         "codigo_ds160": "AA0000000  - solicitante 2\nAA00000002 - novo"})
    corpo = client.get(f"/processos-obt/{linha['id']}").json()
    assert corpo["codigos_ds160"][0] == {"codigo": "AA0000000", "solicitante": "solicitante 2"}
    assert len(corpo["codigos_ds160"]) == 2


def test_nota_adicionar_e_acrescentar(client, processo):
    primeira = client.post(f"{processo}/notas-ds160", json={"texto": "  trocar endereço  "})
    assert primeira.status_code == 201 and primeira.json()["notas_ds160"] == "trocar endereço"
    segunda = client.post(f"{processo}/notas-ds160", json={"texto": "incluir passaporte novo"})
    assert segunda.json()["notas_ds160"] == "trocar endereço\nincluir passaporte novo"


def test_nota_nao_aceita_linha_de_codigo(client, processo):
    assert client.post(f"{processo}/notas-ds160", json={"texto": "AA00000001 - Maria"}).status_code == 422
    assert client.post(f"{processo}/notas-ds160", json={"texto": "  "}).status_code == 422
    client.post(f"{processo}/notas-ds160", json={"texto": "trocar endereço"})
    resposta = client.patch(f"{processo}/notas-ds160", json={"trecho": "trocar", "novo": "aa00000001 - Maria"})
    assert resposta.status_code == 422


def test_nota_edita_so_o_trecho_e_preserva_o_resto(client, processo):
    client.post(f"{processo}/notas-ds160", json={"texto": "trocar endereço"})
    client.post(f"{processo}/notas-ds160", json={"texto": "incluir passaporte novo"})
    resposta = client.patch(f"{processo}/notas-ds160", json={"trecho": "endereço", "novo": "telefone"})
    assert resposta.json()["notas_ds160"] == "trocar telefone\nincluir passaporte novo"


def test_nota_trecho_inexistente_ou_repetido_nao_altera_nada(client, processo):
    client.post(f"{processo}/notas-ds160", json={"texto": "ajustar nome"})
    client.post(f"{processo}/notas-ds160", json={"texto": "ajustar data"})
    assert client.patch(f"{processo}/notas-ds160", json={"trecho": "xyz", "novo": "a"}).status_code == 404
    assert client.patch(f"{processo}/notas-ds160", json={"trecho": "ajustar", "novo": "a"}).status_code == 409
    assert client.get(processo).json()["notas_ds160"] == "ajustar nome\najustar data"


def test_nota_trecho_apagado_por_inteiro_vira_null(client, processo):
    client.post(f"{processo}/notas-ds160", json={"texto": "ajustar nome"})
    resposta = client.patch(f"{processo}/notas-ds160", json={"trecho": "ajustar nome", "novo": ""})
    assert resposta.status_code == 200 and resposta.json()["notas_ds160"] is None


def test_nota_limpar(client, processo):
    client.post(f"{processo}/notas-ds160", json={"texto": "ajustar nome"})
    assert client.delete(f"{processo}/notas-ds160").json()["notas_ds160"] is None
    assert client.delete(f"{processo}/notas-ds160").status_code == 200  # limpar o que já está vazio é inofensivo


def test_patch_geral_nao_aceita_nem_apaga_codigos_e_notas(client, processo):
    adiciona(client, processo, "AA00000001", "Maria")
    client.post(f"{processo}/notas-ds160", json={"texto": "ajustar nome"})
    for campo in ("codigo_ds160", "notas_ds160", "codigos_ds160"):
        assert client.patch(processo, json={campo: "x"}).status_code == 422
    resposta = client.patch(processo, json={"n_solicitantes": 3})  # editar outro campo preserva o DS-160
    assert resposta.status_code == 200
    assert resposta.json()["codigos_ds160"] == [{"codigo": "AA00000001", "solicitante": "Maria"}]
    assert resposta.json()["notas_ds160"] == "ajustar nome"


def test_post_do_processo_nao_aceita_codigos_e_notas(client, cliente):
    resposta = client.post("/processos-obt", json=payload_obt(cliente["id"], notas_ds160="x"))
    assert resposta.status_code == 422


def test_processo_inexistente_da_404(client):
    assert client.post("/processos-obt/99/codigos-ds160",
                       json={"codigo": "AA00000001", "solicitante": "Maria"}).status_code == 404
    assert client.post("/processos-ren/99/notas-ds160", json={"texto": "x"}).status_code == 404


def test_busca_por_trecho_do_codigo(client, cliente):
    a = client.post("/processos-obt", json=payload_obt(cliente["id"])).json()
    client.post("/processos-obt", json=payload_obt(cliente["id"]))
    adiciona(client, f"/processos-obt/{a['id']}", "AA00ABC123", "Maria")
    achados = client.get("/processos-obt", params={"codigo_ds160": "abc123"}).json()
    assert [p["id"] for p in achados] == [a["id"]]
    assert client.get("/processos-obt", params={"codigo_ds160": "zzz"}).json() == []
