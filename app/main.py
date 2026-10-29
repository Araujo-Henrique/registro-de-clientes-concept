from fastapi import FastAPI

from app import store
from app.routers import clientes, funcionarios, passaportes, processos_obt, processos_ren
from app.routers.ds160 import rotas_ds160
from app.schemas.processo_obt import ProcessoOBTOut
from app.schemas.processo_ren import ProcessoRENOut

app = FastAPI(title="Concept Client Registry")

app.include_router(clientes.router)
app.include_router(processos_obt.router)
app.include_router(processos_ren.router)
app.include_router(passaportes.router)
app.include_router(funcionarios.router)
app.include_router(rotas_ds160("/processos-obt", store.processos_obt, ProcessoOBTOut,
                               "Processo de obtenção", "DS-160 do processo de obtenção (OBT)"))
app.include_router(rotas_ds160("/processos-ren", store.processos_ren, ProcessoRENOut,
                               "Processo de renovação", "DS-160 do processo de renovação (REN)"))
