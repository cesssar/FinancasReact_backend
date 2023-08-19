from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from classes.models import *
from classes.schemas import *
from classes.excecoes import *

def get_usuarios(session: Session, limit: int, offset: int) -> List[Usuario]:
    return session.query(Usuario).offset(offset).limit(limit).all()

def get_categorias(session: Session, id_usuario: int) -> List[Categoria]:
    return session.query(Categoria).filter_by(id_usuario=id_usuario).all()

def get_contas(session: Session, id_usuario: int) -> List[Conta]:
    return session.query(Conta).filter_by(id_usuario=id_usuario).all()

def get_cartaocredito(session: Session, id_usuario: int) -> List[CartaoCredito]:
    return session.query(CartaoCredito).filter_by(id_usuario=id_usuario).all()

def get_saldo_contascorrente(session: Session, id_usuario: int) -> float:
    return session.query(func.sum(Conta.saldo)).filter_by(id_usuario=id_usuario).all()[0][0]

def get_saldo_faturas(session: Session, id_usuario: int) -> float:
    return session.query(func.sum(CartaoCredito.fatura_atual)).filter_by(id_usuario=id_usuario).all()[0][0]

def get_saldo_limite(session: Session, id_usuario: int) -> float:
    return session.query(func.sum(CartaoCredito.limite)).filter_by(id_usuario=id_usuario).all()[0][0]

def add_conta(session: Session, conta: ContaAdicionarAtualizar) -> Conta:
    #consulta = session.query(Conta).filter(Conta.banco == conta.banco).first()
    #if consulta is not None:
    #    raise CadastroExistente
    
    nova_conta = Conta(**conta.model_dump())
    session.add(nova_conta)
    session.commit()
    session.refresh(nova_conta)
    return nova_conta