from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg import OperationalError
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from psycopg_pool import PoolTimeout

from app import db, store
from app.routers import clientes, funcionarios, passaportes, processos_obt, processos_ren
from app.routers.ds160 import rotas_ds160
from app.schemas.processo_obt import ProcessoOBTOut
from app.schemas.processo_ren import ProcessoRENOut


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # abre o pool ao ligar o servidor e fecha ao desligar
    abriu = db.abrir()
    yield
    if abriu:
        db.fechar()


app = FastAPI(title="Concept Client Registry", lifespan=ciclo_de_vida)

app.include_router(clientes.router)
app.include_router(processos_obt.router)
app.include_router(processos_ren.router)
app.include_router(passaportes.router)
app.include_router(funcionarios.router)
app.include_router(rotas_ds160("/processos-obt", store.processos_obt, ProcessoOBTOut,
                               "Processo de obtenção", "DS-160 do processo de obtenção (OBT)"))
app.include_router(rotas_ds160("/processos-ren", store.processos_ren, ProcessoRENOut,
                               "Processo de renovação", "DS-160 do processo de renovação (REN)"))


# Rede de segurança: as rotas já checam nome repetido e vínculos antes de gravar, mas duas requisições
# simultâneas podem passar pela checagem ao mesmo tempo. Aí quem decide é o banco, e traduzimos o erro dele.
@app.exception_handler(UniqueViolation)
def registro_duplicado(request: Request, erro: UniqueViolation):
    return JSONResponse(status_code=409, content={"detail": "Já existe um registro com esses dados"})


@app.exception_handler(ForeignKeyViolation)
def registro_vinculado(request: Request, erro: ForeignKeyViolation):
    return JSONResponse(status_code=409,
                        content={"detail": "O registro está vinculado a outros ou o vínculo não existe"})


@app.exception_handler(OperationalError)
@app.exception_handler(PoolTimeout)
def banco_indisponivel(request: Request, erro: Exception):
    return JSONResponse(status_code=503, content={"detail": "Banco de dados indisponível"})
