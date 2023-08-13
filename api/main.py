from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from mock import *
from classes.database import *
from classes.models import *
from classes.schemas import *
from classes.crud import *

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session: Session = SessionLocal()

@app.get("/usuarios/", response_model=UsuarioInfo, tags=["API"])
def lista_usuarios(limit: int = 10, offset: int = 0):
    lista = get_usuarios(session, limit, offset)
    return {"limit": limit, "offset": offset, "data": lista}

@app.get("/categorias/", response_model=CategoriaInfo, tags=["API"])
def lista_categorias(id_usuario: int):
    lista = get_categorias(session, id_usuario)
    return {"data" : lista}

@app.get("/contas/", response_model=ContaInfo, tags=["API"])
def lista_contas(id_usuario: int):
    lista = get_contas(session, id_usuario)
    return {"data" : lista}

@app.get("/cartoescredito/", response_model=CartaoCreditoInfo, tags=["API"])
def lista_cartoes_credito(id_usuario: int):
    lista = get_cartaocredito(session, id_usuario)
    return {"data" : lista}





@app.get("/saldos/contacorrente", tags=["Saldos"])
def saldo_conta_corrente():
    return {"saldo" : saldos["contacorrente"]}

@app.get("/saldos/faturascredito", tags=["Saldos"])
def faturas_credito():
    return {"saldo" : saldos["faturascredito"]}

@app.get("/saldos/limitecredito", tags=["Saldos"])
def limite_credito():
    return {"saldo" : saldos["limitecredito"]}

@app.get("/saldos/limitealimentacao", tags=["Saldos"])
def limite_alimentacao():
    return {"saldo" : saldos["limitealimentacao"]}

@app.delete("/contas/debitaconta/{valor}", tags=["Contas"])
def debita_conta(valor: float):
    if saldos["contacorrente"] > valor:
        saldos["contacorrente"] -= valor
        return {"saldo": saldos["contacorrente"]}
    else:
        return {"message": "saldo insuficiente"}

@app.put("/contas/lancacredito/{valor}", tags=["Contas"])
def lanca_credito(valor: float):
    if saldos["limitecredito"] > valor:
        saldos["faturascredito"] += valor
        saldos["limitecredito"] -= valor
        return {"saldo": saldos["faturascredito"]}
    else:
        return {"message": "limite de crédito insuficiente"}

@app.delete("/contas/debitaalimentacao/{valor}", tags=["Contas"])
def debita_conta(valor: float):
    if saldos["limitealimentacao"] > valor:
        saldos["limitealimentacao"] -= valor
        return {"saldo": saldos["limitealimentacao"]}
    else:
        return {"message": "saldo insuficiente"}

@app.put("/contas/pagafatura/{valor}", tags=["Contas"])
def lanca_credito(valor: float):
    saldos["limitecredito"] += valor
    return {"saldo": saldos["limitecredito"]}