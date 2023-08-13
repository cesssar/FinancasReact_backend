from pydantic import BaseModel
from typing import List
import datetime

class UsuarioBase(BaseModel):
    id: int | None = None
    login: str
    nome: str
    
class UsuarioSchema(UsuarioBase):
    senha: str
    
    class Config:
        from_attributes = True
        populate_by_name= True
        arbitrary_types_allowed = True

class UsuarioInfo(BaseModel):
    limit: int
    offset: int
    data: List[UsuarioBase]


class CategoriaSchema(BaseModel):
    id: int
    id_usuario: int
    categoria: str

    class Config:
        from_attributes = True
        populate_by_name= True
        arbitrary_types_allowed = True

class CategoriaInfo(BaseModel):
    data: List[CategoriaSchema]


class CartaoCreditoSchema(BaseModel):
    id: int
    id_usuario: int
    banco: str
    limite: float
    fatura_atual: float
    dia_corte: int

    class Config:
        from_attributes = True
        populate_by_name= True
        arbitrary_types_allowed = True

class CartaoCreditoInfo(BaseModel):
    data: List[CartaoCreditoSchema]


class ContaSchema(BaseModel):
    id: int
    id_usuario: int
    banco: str
    saldo: str

    class Config:
        from_attributes = True
        populate_by_name= True
        arbitrary_types_allowed = True

class ContaInfo(BaseModel):
    data: List[ContaSchema]


class TransacaoSchema(BaseModel):
    id: int
    data: datetime.datetime
    id_conta: int
    id_credito: int
    id_categoria: int
    numero_parcelas: int
    valor: float

    class Config:
        from_attributes = True
        populate_by_name= True
        arbitrary_types_allowed = True

class TransacaoInfo(BaseModel):
    data: List[TransacaoSchema]