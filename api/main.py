from fastapi import FastAPI, status, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from mock import *
from classes.database import *
from classes.models import *
from classes.schemas import *
from classes.excecoes import *
from classes.repositories import *

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


@app.get("/cadastros/conta", response_model=list[ContaResponse], tags=["API"])
def listar_conta(db: Session = Depends(get_db)):
    contas = ContaRepository.listar(db)
    return [ContaResponse.from_orm(conta) for conta in contas]

@app.post("/cadastros/conta", response_model=ContaResponse, status_code=status.HTTP_201_CREATED, tags=["API"])
def criar_conta(request: ContaRequest, db: Session = Depends(get_db)):
    conta = ContaRepository.salvar(db, Conta(**request.model_dump()))
    return ContaResponse.from_orm(conta)

@app.delete("/cadastros/conta/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["API"])
def delete_conta(id: int, db: Session = Depends(get_db)):
    if not ContaRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada" 
        )
    if not ContaRepository.deletar(db, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Conta com saldo positivo"
        )
    return Response(status_code=status.HTTP_200_OK)

@app.put("/cadastros/conta/{id}/{valor}", tags=["API"])
def debitar_creditar(id: int, valor: float, db: Session = Depends(get_db)):
    if not ContaRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada" 
        )
    if not ContaRepository.debitar_creditar(db, id, valor):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Conta com saldo insuficiente"
        )
    return Response(status_code=status.HTTP_200_OK)


@app.get("/cadastros/cartaocredito", response_model=list[CartaoCreditoResponse], tags=["API"])
def listar_cartaocredito(db: Session = Depends(get_db)):
    contas = CartaoCreditoRepository.listar(db)
    return [CartaoCreditoResponse.from_orm(conta) for conta in contas]

@app.post("/cadastros/cartaocredito", response_model=CartaoCreditoResponse, status_code=status.HTTP_201_CREATED, tags=["API"])
def criar_cartao(request: CartaoCreditoRequest, db: Session = Depends(get_db)):
    conta = CartaoCreditoRepository.salvar(db, Conta(**request.model_dump()))
    return CartaoCreditoRepository.from_orm(conta)

@app.delete("/cadastros/cartaocredito/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["API"])
def delete_cartao(id: int, db: Session = Depends(get_db)):
    if not CartaoCreditoRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Cartão não localizado" 
        )
    if not CartaoCreditoRepository.deletar(db, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cartão com limite e/ou com fatura"
        )
    return Response(status_code=status.HTTP_200_OK)

@app.put("/cadastros/cartaocredito/{id}/{valor}", tags=["API"])
def lancar(id: int, valor: float, db: Session = Depends(get_db)):
    if not CartaoCreditoRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Cartão não localizado" 
        )
    if not CartaoCreditoRepository.lancar(db, id, valor):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cartão com limite insuficiente"
        )
    return Response(status_code=status.HTTP_200_OK)

@app.put("/cadastros/cartaocredito/pagarfatura/{id}/{valor}", tags=["API"])
def pagar(id: int, valor: float, db: Session = Depends(get_db)):
    if not CartaoCreditoRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Cartão não localizado" 
        )
    if not CartaoCreditoRepository.pagar(db, id, valor):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Valor superior ao valor da fatura"
        )
    return Response(status_code=status.HTTP_200_OK)



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