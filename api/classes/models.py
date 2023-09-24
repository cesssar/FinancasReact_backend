from sqlalchemy import Column, Integer, String, Float, Date

from classes.database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String, unique=True)
    nome = Column(String, unique=True)
    senha = Column(String)

class CartaoCredito(Base):
    __tablename__ = "cartaocredito"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer)
    banco = Column(String)
    limite = Column(Float)
    fatura_atual = Column(Float)
    dia_corte = Column(Integer)
    tipo = Column(String)

class TipoCartao(Base):
    __tablename__ = "tipocartao"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descricao = Column(String)

class Categoria(Base):
    __tablename__ = "categoria"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer)
    categoria = Column(String)

class Conta(Base):
    __tablename__ = "conta"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer)
    banco = Column(String)
    saldo = Column(Float)

class Lancamento(Base):
    __tablename__ = "lancamento"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data = Column(Date)
    id_conta = Column(Integer)
    id_credito = Column(Integer)
    id_categoria = Column(Integer)
    valor = Column(Float)
    observacao = Column(String)
    id_usuario = Column(Integer)

