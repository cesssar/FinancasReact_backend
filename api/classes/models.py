from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from classes.database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True)
    nome = Column(String, unique=True)
    senha = Column(String)

class CartaoCredito(Base):
    __tablename__ = "cartaocredito"
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer)
    banco = Column(String)
    limite = Column(Float)
    fatura_atual = Column(Float)
    dia_corte = Column(Integer)

class Categoria(Base):
    __tablename__ = "categoria"
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer)
    categoria = Column(String)

class Conta(Base):
    __tablename__ = "conta"
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer)
    banco = Column(String)
    saldo = Column(Float)

class Transacao(Base):
    __tablename__ = "transacao"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(DateTime)
    id_conta = Column(Integer)
    id_credito = Column(Integer)
    id_categoria = Column(Integer)
    numero_parcelas = Column(Integer)
    valor = Column(Float)

