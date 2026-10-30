# Concept Client Registry

API de registro de clientes e processos de visto da Concept Vistos, feita em Python, FastAPI e PostgreSQL.

## Problema a ser solucionado
Os registros da empresa são mantidos em planilhas do Google Sheets. A intenção deste projeto é tirar essa dependência e permitir que a empresa tenha o seu próprio sistema de registros, através de uma aplicação backend.

## Objetivo
Um sistema de registro, edição, consulta e remoção de clientes com o acompanhamento dos processos (obtenção, renovação e passaporte). Eventualmente ele terá um dashboard e visualização para os clientes; nesta primeira etapa o foco é a API e o banco de dados.

> Todos os dados de exemplo deste repositório são fictícios. Nenhum dado real de cliente faz parte do projeto.

## Tecnologias
- Python 3.14
- FastAPI (API REST) e Uvicorn (servidor)
- Pydantic v2 (validação dos dados)
- PostgreSQL 18
- psycopg 3 (acesso ao banco com SQL direto) e psycopg_pool (pool de conexões)
- pytest (testes)

## O que a API faz
| Recurso | Rotas | Observações |
|---|---|---|
| Clientes | `/clientes` | CRUD, busca por nome (trecho), grupo e telefone |
| Processos de obtenção (OBT) | `/processos-obt` | CRUD e filtros por cliente, consulado, situação, monitoramento e código do DS-160 |
| Processos de renovação (REN) | `/processos-ren` | CRUD e filtros; `data_despacho` é calculada (CASV − 7 dias) |
| Passaportes | `/passaportes` | CRUD e filtros por cliente e situação |
| Funcionários | `/funcionarios` | Consulta (ativos e inativos) |
| DS-160 | `/processos-obt/{id}/codigos-ds160`, `/processos-obt/{id}/notas-ds160` (e o mesmo em `/processos-ren`) | Códigos dos formulários e notas de alteração; veja abaixo |

A documentação interativa (Swagger) fica em `http://127.0.0.1:8000/docs` com o servidor ligado.

### DS-160: códigos e notas
Nas planilhas, a célula do DS-160 tinha uma nota com o código do formulário de cada solicitante (`AA00000001 - Maria`, e `novo` no lugar do nome quando o formulário é refeito) e, às vezes, pedidos de alteração sem padrão. No banco isso virou duas colunas de texto:

- `codigo_ds160`: só as linhas de código, uma por formulário. A API recebe o código e o solicitante em campos separados, valida o formato (`AA00` + 6 letras ou números) e devolve uma lista (`codigos_ds160`).
- `notas_ds160`: o restante da nota (as alterações).

As rotas de DS-160 alteram só o que foi pedido, sem sobrescrever o resto: adicionar, editar e remover um código (identificado pelo próprio código); acrescentar, trocar um trecho ou limpar a nota. Se duas pessoas editam o mesmo processo ao mesmo tempo, a segunda recebe 409 e repete a operação. O `PATCH` geral do processo não mexe nessas colunas.

## Regras de negócio
- O nome do cliente é único, sem diferenciar maiúsculas de minúsculas. O telefone pode se repetir (famílias e agências compartilham número).
- O telefone é guardado só com dígitos, sem o 55 do Brasil.
- Cliente com processos ou passaportes vinculados não pode ser apagado (409).
- Consulado `N/D` existe só no histórico antigo; cadastros novos precisam informar o consulado.
- Orientação "Agendada" exige a data da orientação.
- Os erros seguem o padrão: 404 para registro inexistente, 409 para conflito (duplicidade, vínculo ou edição simultânea), 422 para dado inválido e 503 se o banco estiver fora do ar.

## Estrutura do projeto
```
app/
  main.py          orquestra: monta a aplicação, rotas e tratamento de erros do banco
  db.py            conexão com o PostgreSQL (pool)
  store.py         acesso às tabelas (SQL com parâmetros)
  enums.py         valores permitidos (consulado, situação, ...)
  routers/         rotas de cada recurso
  schemas/         modelos Pydantic (validação de entrada e formato de saída)
db/                scripts SQL (veja abaixo)
tests/             testes automatizados
```

## Como rodar
1. Crie o ambiente virtual e instale as dependências:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Crie o banco no PostgreSQL (por exemplo `concept_client_registry`) e rode, nesta ordem, `db/01_schema.sql` e `db/02_processos_ren.sql`.
3. Copie `.env.example` para `.env` e preencha `DATABASE_URL` com o usuário, a senha e o banco. O arquivo `.env` não vai para o git.
4. Suba a API:
   ```
   uvicorn app.main:app --reload --env-file .env
   ```

## Banco de dados
Os scripts da pasta `db/` rodam em ordem:

| Script | Para quê |
|---|---|
| `01_schema.sql`, `02_processos_ren.sql` | Criam as tabelas, regras (CHECK) e índices. **Só estes dois são necessários para uma instalação nova.** |
| `03` a `10` | Importam as planilhas antigas: tabelas de apoio (staging) com o CSV bruto, funções de limpeza e as cargas para as tabelas finais |
| `legacy/` | Ajustes (`ALTER`) para bancos criados com versões antigas do esquema |

A importação das planilhas é um processo único de migração e não faz parte da API. O Apps Script `db/apps_script_notas_ds160.gs` copia as notas das células do DS-160 para uma coluna, porque o CSV exportado do Google Sheets não traz as notas.

## Testes
Os testes rodam contra um PostgreSQL de verdade, num banco só de testes (o esquema é recriado a cada execução):

```
createdb concept_client_registry_test
set TEST_DATABASE_URL=postgresql://USUARIO:SENHA@localhost:5432/concept_client_registry_test
pytest
```

O nome do banco de teste precisa terminar em `_test`; os testes recusam qualquer outro, para nunca apagar o banco real.

## Aprendizados desta etapa
Python, HTTP e APIs REST, FastAPI, Pydantic (validação, enums, campos calculados), SQL e modelagem no PostgreSQL (CHECK, chaves estrangeiras, colunas geradas, índices), limpeza e carga de dados com tabelas de apoio, acesso ao banco com psycopg (parâmetros contra SQL injection, pool de conexões), testes com pytest e Git.

## Próximos passos
- Projeto 2 (Concept Visa Workflow): modelagem relacional mais ampla, SQLAlchemy, migrations, autenticação e permissões.
- Front-end (dashboard), depois que a API tiver autenticação.
