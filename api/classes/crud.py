from typing import List
from sqlalchemy.orm import Session

from classes.models import *
from classes.schemas import *

def get_usuarios(session: Session, limit: int, offset: int) -> List[Usuario]:
    return session.query(Usuario).offset(offset).limit(limit).all()

def get_categorias(session: Session, id_usuario: int) -> List[Categoria]:
    return session.query(Categoria).filter_by(id_usuario=id_usuario).all()

def get_contas(session: Session, id_usuario: int) -> List[Conta]:
    return session.query(Conta).filter_by(id_usuario=id_usuario).all()

def get_cartaocredito(session: Session, id_usuario: int) -> List[CartaoCredito]:
    return session.query(CartaoCredito).filter_by(id_usuario=id_usuario).all()