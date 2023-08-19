from sqlalchemy.orm import Session

from classes.models import *

class ContaRepository:

    @staticmethod
    def listar(db: Session) -> list[Conta]:
        return db.query(Conta).all()
    
    @staticmethod
    def salvar(db: Session, conta: Conta) -> Conta:
        if conta.id:
            db.merge(conta)
        else:
            db.add(conta)
        db.commit()
        return conta
    
    @staticmethod
    def deletar(db: Session, id: int) -> bool:
        conta = db.query(Conta).filter(Conta.id == id).first()
        if conta is not None and conta.saldo == 0.0:
            db.delete(conta)
            db.commit()
            return True
        return False
        
    @staticmethod
    def localizar(db: Session, id: int) -> Conta:
        return db.query(Conta).filter(Conta.id == id).first()

    @staticmethod
    def debitar_creditar(db: Session, id: int, valor: float) -> bool:
        conta = db.query(Conta).filter(Conta.id == id).first()
        if conta is not None and (valor < 0 and conta.saldo >= abs(valor)) or (valor > 0):
            conta.saldo += valor
            db.merge(conta)
            db.commit()
            return True
        return False
    

class CartaoCreditoRepository:

    @staticmethod
    def listar(db: Session) -> list[CartaoCredito]:
        return db.query(CartaoCredito).all()
    
    @staticmethod
    def salvar(db: Session, cartao: CartaoCredito) -> CartaoCredito:
        if cartao.id:
            db.merge(cartao)
        else:
            db.add(cartao)
        db.commit()
        return cartao
    
    @staticmethod
    def deletar(db: Session, id: int) -> bool:
        cartao = db.query(CartaoCredito).filter(CartaoCredito.id == id).first()
        if cartao is not None and cartao.limite == 0.0 and cartao.fatura_atual == 0.0:
            db.delete(cartao)
            db.commit()
            return True
        return False
        
    @staticmethod
    def localizar(db: Session, id: int) -> CartaoCredito:
        return db.query(CartaoCredito).filter(CartaoCredito.id == id).first()
    
    @staticmethod
    def lancar(db: Session, id: int, valor: float) -> bool:
        cartao = db.query(CartaoCredito).filter(CartaoCredito.id == id).first()
        if cartao is not None and cartao.limite >= valor and valor >0:
            cartao.limite -= valor
            cartao.fatura_atual += valor
            db.merge(cartao)
            db.commit()
            return True
        return False
    
    @staticmethod
    def pagar(db: Session, id: int, valor: float) -> bool:
        cartao = db.query(CartaoCredito).filter(CartaoCredito.id == id).first()
        if cartao is not None and valor <= cartao.fatura_atual and valor >0:
            cartao.limite += valor
            cartao.fatura_atual -= valor
            db.merge(cartao)
            db.commit()
            return True
        return False
