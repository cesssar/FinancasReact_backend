from fastapi import FastAPI, status, Depends, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import os

from classes.database import *
from classes.models import *
from classes.schemas import *
from classes.repositories import *

from auth.auth_bearer import *
from auth.auth_handler import *
from auth.model import *

load_dotenv('.env')

app = FastAPI(
    title="Backend para o front React",
    version="1.0.0",
    contact={
        "name": "Cesar Steinmeier",
        "email": "cesssar@me.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

#inicializa usuário
users = []

users.append(UserSchema(
    email = os.environ["email"],
    password = os.environ["password"]
))

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

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

@app.post("/login", tags=["Autenticação"], summary="Gera token para demais endpoints")
async def login_user(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/cadastros/conta", response_model=list[ContaResponse], tags=["Conta"],  summary="Lista as contas cadastradas", dependencies=[Depends(JWTBearer())])
def listar_conta(db: Session = Depends(get_db)):
    contas = ContaRepository.listar(db)
    return [ContaResponse.from_orm(conta) for conta in contas]

@app.post("/cadastros/conta", response_model=ContaResponse, status_code=status.HTTP_201_CREATED, tags=["Conta"],  summary="Cadastra uma nova conta", dependencies=[Depends(JWTBearer())])
def criar_conta(request: ContaRequest, db: Session = Depends(get_db)):
    conta = ContaRepository.salvar(db, Conta(**request.model_dump()))
    return ContaResponse.from_orm(conta)

@app.delete("/cadastros/conta/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Conta"],  summary="Deleta uma conta desde que zerada e não esteja em uso", dependencies=[Depends(JWTBearer())])
def deletar_conta(id: int, db: Session = Depends(get_db)):
    if not ContaRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada" 
        )
    if not ContaRepository.deletar(db, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Conta com saldo positivo ou com registro de lançamento"
        )
    return Response(status_code=status.HTTP_200_OK)

@app.put("/cadastros/conta/{id}/{valor}", tags=["Conta"],  summary="Debita ou credita um valor a uma conta", dependencies=[Depends(JWTBearer())])
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



@app.get("/cadastros/cartaocredito", response_model=list[CartaoCreditoResponse], tags=["Cartão Crédito"],  summary="Lista os cartões de crédito cadastrados", dependencies=[Depends(JWTBearer())])
def listar_cartaocredito(db: Session = Depends(get_db)):
    contas = CartaoCreditoRepository.listar(db)
    return [CartaoCreditoResponse.from_orm(conta) for conta in contas]

@app.post("/cadastros/cartaocredito", response_model=CartaoCreditoResponse, status_code=status.HTTP_201_CREATED, tags=["Cartão Crédito"],  summary="Cadastra um novo cartão de crédito", dependencies=[Depends(JWTBearer())])
def criar_cartao(request: CartaoCreditoRequest, db: Session = Depends(get_db)):
    conta = CartaoCreditoRepository.salvar(db, Conta(**request.model_dump()))
    return CartaoCreditoRepository.from_orm(conta)

@app.delete("/cadastros/cartaocredito/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cartão Crédito"],  summary="Deleta um cartão de crédito zerado e sem lançamentos", dependencies=[Depends(JWTBearer())])
def deletar_cartao(id: int, db: Session = Depends(get_db)):
    if not CartaoCreditoRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Cartão não localizado" 
        )
    if not CartaoCreditoRepository.deletar(db, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cartão com limite e/ou com fatura ou com registro de lançamento"
        )
    return Response(status_code=status.HTTP_200_OK)

@app.put("/cadastros/cartaocredito/{id}/{valor}", tags=["Cartão Crédito"],  summary="Lança uma compra/despesa em um cartão de crédito", dependencies=[Depends(JWTBearer())])
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

@app.put("/cadastros/cartaocredito/pagarfatura/{id}/{valor}", tags=["Cartão Crédito"],  summary="Informa pagamento da fatura recompondo limite", dependencies=[Depends(JWTBearer())])
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



@app.get("/cadastros/categoria", response_model=list[CategoriaResponse], tags=["Categoria"],  summary="Lista as categorias cadastradas", dependencies=[Depends(JWTBearer())])
def listar_categoria(db: Session = Depends(get_db)):
    categorias = CategoriaRepository.listar(db)
    return [CategoriaResponse.from_orm(categoria) for categoria in categorias]

@app.post("/cadastros/categoria", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED, tags=["Categoria"],  summary="Cadastra uma nova categoria", dependencies=[Depends(JWTBearer())])
def criar_categoria(request: CategoriaRequest, db: Session = Depends(get_db)):
    categoria = CategoriaRepository.salvar(db, Categoria(**request.model_dump()))
    return CategoriaResponse.from_orm(categoria)

@app.delete("/cadastros/categoria/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Categoria"],  summary="Deleta uma categoria sem uso", dependencies=[Depends(JWTBearer())])
def deletar_categoria(id: int, db: Session = Depends(get_db)):
    if not CategoriaRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não localizada" 
        )
    if not CategoriaRepository.deletar(db, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Categoria com registro de lançamento"
        )
    return Response(status_code=status.HTTP_200_OK)



@app.get("/cadastros/lancamento/{mes}/{ano}", tags=["Lançamento"],  summary="Lista os lançamentos cadastrados", dependencies=[Depends(JWTBearer())])
def listar_lancamento(mes: int, ano: int, db: Session = Depends(get_db)):
    l = LancamentoRepository.listar(db, mes, ano)
    return jsonable_encoder(l)

@app.post("/cadastros/lancamento", status_code=status.HTTP_201_CREATED, tags=["Lançamento"],  summary="Cadatra um novo lançamento", dependencies=[Depends(JWTBearer())])
def criar_lancamento(request: LancamentoRequest, db: Session = Depends(get_db)):
    lancamento = LancamentoRepository.salvar(db, Lancamento(**request.model_dump()))
    if lancamento != "ok":
        raise HTTPException(
           status_code=status.HTTP_412_PRECONDITION_FAILED, detail=lancamento
        )
    return Response(status_code=status.HTTP_201_CREATED)

@app.delete("/cadastros/lancamento/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Lançamento"],  summary="Deleta uma categoria sem uso", dependencies=[Depends(JWTBearer())])
def deletar_lancamento(id: int, db: Session = Depends(get_db)):
    if not LancamentoRepository.localizar(db, id):
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="Lançamento não localizado" 
        )
    if not LancamentoRepository.deletar(db, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Houve um erro ao tentar deletar o lançamento"
        )
    return Response(status_code=status.HTTP_200_OK)