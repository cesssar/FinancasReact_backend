from pydantic import BaseModel
import datetime

class UsuarioBase(BaseModel):
    login: str
    nome: str
    
class UsuarioSchema(UsuarioBase):
    senha: str


class UsuarioRequest(UsuarioSchema):
    ...

class UsuarioResponse(UsuarioBase):
    id: int 
    class Config:
        from_attributes = True


class ContaBase(BaseModel):
    id_usuario: int
    banco: str
    saldo: float

class ContaRequest(ContaBase):
    ...

class ContaResponse(ContaBase):
    id: int
    class Config:
        from_attributes = True


class CartaoCreditoBase(BaseModel):
    id_usuario: int
    banco: str
    limite: float
    fatura_atual: float
    dia_corte: int

class CartaoCreditoRequest(CartaoCreditoBase):
    ...

class CartaoCreditoResponse(CartaoCreditoBase):
    id: int
    class Config:
        from_attributes = True