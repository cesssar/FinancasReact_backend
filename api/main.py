from fastapi import FastAPI, status, Depends, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv

from classes.database import *
from classes.models import *
from classes.schemas import *
from classes.repositories import *
from classes.extrairdados import *

from auth.auth_bearer import *
from auth.auth_handler import *

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

def get_userId(db: Session, request: Request):
    token = request.headers.get('Authorization').replace('Bearer ', '')
    usuario = decodeJWT(token)['user']
    id = UsuarioRepository.getId(db, usuario)
    return id

@app.get("/backend/")
async def root():
    return {"message": "Backend para o front React"}

@app.post("/backend/login", tags=["Autenticação"], summary="Gera token para demais endpoints")
async def login_user(db: Session = Depends(get_db),user: UsuarioLogin = Body(...)):
    id = UsuarioRepository.login(db, user.login, user.senha)
    if id:
        return signJWT(user.login)
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@app.get("/backend/saldo/contas", tags=["Conta"],  summary="Retorna saldo das contas", dependencies=[Depends(JWTBearer())])
def saldo_contas(r: Request, db: Session = Depends(get_db)) -> float:
    id_usuario = get_userId(db, r)
    saldo = ContaRepository.saldo(db, id_usuario)
    return jsonable_encoder(saldo)

@app.get("/backend/cadastros/conta", response_model=list[ContaResponse], tags=["Conta"],  summary="Lista as contas cadastradas", dependencies=[Depends(JWTBearer())])
def listar_conta(r: Request,db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    contas = ContaRepository.listar(db, id_usuario)
    return [ContaResponse.from_orm(conta) for conta in contas]

@app.get("/backend/cadastros/conta/{id}", tags=["Conta"],  summary="Retorna detalhes de uma conta", dependencies=[Depends(JWTBearer())])
def get_lancamento(id: int, db: Session = Depends(get_db)):
    c = ContaRepository.get_conta(db, id)
    return jsonable_encoder(c)

@app.post("/backend/cadastros/conta", response_model=ContaResponse, status_code=status.HTTP_201_CREATED, tags=["Conta"],  summary="Cadastra uma nova conta", dependencies=[Depends(JWTBearer())])
def criar_conta(r: Request, request: ContaRequest, db: Session = Depends(get_db)):
    c = Conta(**request.model_dump())
    id_usuario = get_userId(db, r)
    c.id_usuario = id_usuario
    conta = ContaRepository.salvar(db, c)
    return ContaResponse.from_orm(conta)

@app.delete("/backend/cadastros/conta/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Conta"],  summary="Deleta uma conta desde que zerada e não esteja em uso", dependencies=[Depends(JWTBearer())])
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

@app.put("/backend/cadastros/conta/{id}/{valor}", tags=["Conta"],  summary="Debita ou credita um valor a uma conta", dependencies=[Depends(JWTBearer())])
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


@app.get("/backend/fatura/cartaocredito", tags=["Cartão Crédito"],  summary="Retorna valor da fatura atual", dependencies=[Depends(JWTBearer())])
def fatura_atual(r: Request,db: Session = Depends(get_db)) -> float:
    id_usuario = get_userId(db, r)
    fatura = CartaoCreditoRepository.fatura_atual(db, id_usuario)
    return jsonable_encoder(fatura)

@app.get("/backend/limite/cartaocredito", tags=["Cartão Crédito"],  summary="Retorna limite disponível", dependencies=[Depends(JWTBearer())])
def limite(r: Request,db: Session = Depends(get_db), tipo: str = 'c') -> float:
    id_usuario = get_userId(db, r)
    limite = CartaoCreditoRepository.limite_credito(db, id_usuario, tipo)
    return jsonable_encoder(limite)

@app.get("/backend/cadastros/cartaocredito", response_model=list[CartaoCreditoResponse], tags=["Cartão Crédito"],  summary="Lista os cartões de crédito cadastrados", dependencies=[Depends(JWTBearer())])
def listar_cartaocredito(r: Request,db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    contas = CartaoCreditoRepository.listar(db, id_usuario)
    return [CartaoCreditoResponse.from_orm(conta) for conta in contas]

@app.get("/backend/cadastros/cartaocredito/{id}", tags=["Cartão Crédito"],  summary="Retorna detalhes de um cartão de crédito", dependencies=[Depends(JWTBearer())])
def get_cartaocredito(id: int, db: Session = Depends(get_db)):
    c = CartaoCreditoRepository.get_cartao(db, id)
    return jsonable_encoder(c)

@app.post("/backend/cadastros/cartaocredito", response_model=CartaoCreditoResponse, status_code=status.HTTP_201_CREATED, tags=["Cartão Crédito"],  summary="Cadastra um novo cartão de crédito", dependencies=[Depends(JWTBearer())])
def criar_cartao(r: Request, request: CartaoCreditoRequest, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    cartao = CartaoCredito(**request.model_dump())
    cartao.id_usuario = id_usuario
    c = CartaoCreditoRepository.salvar(db, cartao)
    return CartaoCreditoResponse.from_orm(c)

@app.delete("/backend/cadastros/cartaocredito/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cartão Crédito"],  summary="Deleta um cartão de crédito zerado e sem lançamentos", dependencies=[Depends(JWTBearer())])
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

@app.put("/backend/cadastros/cartaocredito/{id}/{valor}", tags=["Cartão Crédito"],  summary="Lança uma compra/despesa em um cartão de crédito", dependencies=[Depends(JWTBearer())])
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

@app.put("/backend/cadastros/cartaocredito/pagarfatura/{id}/{valor}", tags=["Cartão Crédito"],  summary="Informa pagamento da fatura recompondo limite", dependencies=[Depends(JWTBearer())])
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



@app.get("/backend/cadastros/categoria", response_model=list[CategoriaResponse], tags=["Categoria"],  summary="Lista as categorias cadastradas", dependencies=[Depends(JWTBearer())])
def listar_categoria(r: Request,db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    categorias = CategoriaRepository.listar(db, id_usuario)
    return [CategoriaResponse.from_orm(categoria) for categoria in categorias]

@app.post("/backend/cadastros/categoria", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED, tags=["Categoria"],  summary="Cadastra uma nova categoria", dependencies=[Depends(JWTBearer())])
def criar_categoria(r: Request, request: CategoriaRequest, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    categoria = Categoria(**request.model_dump())
    categoria.id_usuario = id_usuario
    c = CategoriaRepository.salvar(db, categoria)
    return CategoriaResponse.from_orm(c)

@app.delete("/backend/cadastros/categoria/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Categoria"],  summary="Deleta uma categoria sem uso", dependencies=[Depends(JWTBearer())])
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



@app.get("/backend/cadastros/lancamento/{mes}/{ano}", tags=["Lançamento"],  summary="Lista os lançamentos cadastrados", dependencies=[Depends(JWTBearer())])
def listar_lancamento(r: Request, mes: int, ano: int, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    l = LancamentoRepository.listar(db, mes, ano, id_usuario)
    return jsonable_encoder(l)

@app.get("/backend/cadastros/lancamento/{id}", tags=["Lançamento"],  summary="Retorna detalhes de um lançamento", dependencies=[Depends(JWTBearer())])
def get_lancamento(id: int, db: Session = Depends(get_db)):
    l = LancamentoRepository.get_lancamento(db, id)
    return jsonable_encoder(l)

@app.post("/backend/cadastros/lancamento", status_code=status.HTTP_201_CREATED, tags=["Lançamento"],  summary="Cadatra um novo lançamento", dependencies=[Depends(JWTBearer())])
def criar_lancamento(r: Request, request: LancamentoRequest, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    lancamento = Lancamento(**request.model_dump())
    lancamento.id_usuario = id_usuario
    lancamento = LancamentoRepository.salvar(db, lancamento)
    if lancamento != "ok":
        raise HTTPException(
           status_code=status.HTTP_412_PRECONDITION_FAILED, detail=lancamento
        )
    return Response(status_code=status.HTTP_201_CREATED)

@app.delete("/backend/cadastros/lancamento/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Lançamento"],  summary="Deleta um lançamento", dependencies=[Depends(JWTBearer())])
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

@app.get("/backend/lancamento/ultimos", tags=["Lançamento"],  summary="Recupera últimos sete dias", dependencies=[Depends(JWTBearer())])
def ultimos_dias(r: Request, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    u = LancamentoRepository.get_ultimos_dias(db, id_usuario)
    return jsonable_encoder(u)

@app.get("/backend/lancamento/categoria", tags=["Lançamento"],  summary="Retorna valores gastos por categoria", dependencies=[Depends(JWTBearer())])
def por_categoria(r: Request, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    u = LancamentoRepository.get_por_categoria(db, id_usuario)
    return jsonable_encoder(u)

@app.post("/backend/cadastros/qrcode/" , tags=["Lançamento"],  summary="", dependencies=[Depends(JWTBearer())])
def qrcode(r: Request,request: QrcodeRequest, db: Session = Depends(get_db)):
    id_usuario = get_userId(db, r)
    dados = ExtrairDados(str(request.link)).extrair()
    retorno = LancamentoRepository.salvarQrcode(
        db, dados, id_usuario, request
    )
    return 'Dados importados com sucesso' if retorno else 'Erro ao importar dados'