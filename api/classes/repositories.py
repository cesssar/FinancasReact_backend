from sqlalchemy.orm import Session
from sqlalchemy import extract 

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
        lancamento = db.query(Lancamento).filter(Lancamento.id_conta == id).all()
        if conta is not None and conta.saldo == 0.0 and lancamento is None:
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
        lancamento = db.query(Lancamento).filter(Lancamento.id_credito == id).all()
        if cartao is not None and cartao.limite == 0.0 and cartao.fatura_atual == 0.0 and lancamento is None:
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



class CategoriaRepository:

    @staticmethod
    def listar(db: Session) -> list[Categoria]:
        return db.query(Categoria).all()
    
    @staticmethod
    def localizar(db: Session, id: int) -> Categoria:
        return db.query(Categoria).filter(Categoria.id == id).first()
    
    @staticmethod
    def salvar(db: Session, categoria: Categoria) -> Categoria:
        if categoria.id:
            db.merge(categoria)
        else:
            db.add(categoria)
        db.commit()
        return categoria
    
    @staticmethod
    def deletar(db: Session, id: int) -> bool:
        categoria = db.query(Categoria).filter(Categoria.id == id).first()
        lancamento = db.query(Lancamento).filter(Lancamento.id_categoria == id).all()
        if lancamento is None:
            db.delete(categoria)
            db.commit()
            return True
        return False
    


class LancamentoRepository:

    @staticmethod
    def listar(db: Session, mes: int, ano: int) -> list[Lancamento]:
        lancamentos = []
        result = db.query(Lancamento, Conta, Categoria).filter(Lancamento.id_conta == Conta.id, Categoria.id == Lancamento.id_categoria, extract('month', Lancamento.data) == 8, extract('year', Lancamento.data) == 2023).all()
        for l, c, ca in result:
            linha = {
                "data": l.data.strftime('%Y-%m-%d'),
                "banco": c.banco,
                "categoria": ca.categoria,
                "numero_parcelas": l.numero_parcelas,
                "valor": l.valor,
                "observacao": l.observacao
            }
            lancamentos.append(linha)
        result = db.query(Lancamento, CartaoCredito, Categoria).filter(Lancamento.id_credito == CartaoCredito.id, Categoria.id == Lancamento.id_categoria, extract('month', Lancamento.data) == 8, extract('year', Lancamento.data) == 2023).all()
        for l, c, ca in result:
            linha = {
                "data": l.data.strftime('%Y-%m-%d'),
                "cartao_credito": c.banco,
                "categoria": ca.categoria,
                "numero_parcelas": l.numero_parcelas,
                "valor": l.valor,
                "observacao": l.observacao
            }
            lancamentos.append(linha)
        return lancamentos


    @staticmethod
    def localizar(db: Session, id: int) -> Lancamento:
        return db.query(Lancamento).filter(Lancamento.id == id).first()
    
    @staticmethod
    def salvar(db: Session, lancamento: Lancamento) -> str:
        if lancamento.id:
            db.merge(lancamento)
        else:
            conta = db.query(Conta).filter(Conta.id == lancamento.id_conta).first()
            cartao = db.query(CartaoCredito).filter(CartaoCredito.id == lancamento.id_credito).first()
            catetgoria = db.query(Categoria).filter(Categoria.id == lancamento.id_categoria).first()
            if conta is not None and cartao is not None:
                return "Informar um id_conta válido ou um id_credito válido, mas não ambos."
            elif catetgoria is None:
                return "Categoria não localizada."
            elif lancamento.valor is None or lancamento.valor < 0:
                return "Informar valor superior a zero."
            elif lancamento.numero_parcelas is None or lancamento.numero_parcelas < 0:
                return "Informar no mínimo uma parcela."
            elif conta is not None and conta.saldo < lancamento.valor:
                return "Saldo da conta insuficiente."
            elif cartao is not None and cartao.limite < lancamento.valor:
                return "Limite do cartão insuficiente."
            elif conta is not None:
                if conta.saldo >= lancamento.valor:
                    conta.saldo -= lancamento.valor
                    db.merge(conta)
                    db.commit()
                    db.add(lancamento)
                    db.commit()
                    return "ok"
            elif cartao is not None:
                if cartao.limite >= lancamento.valor:
                    cartao.limite -= lancamento.valor
                    db.merge(cartao)
                    db.commit()
                    db.add(lancamento)
                    db.commit()
                    return "ok"
        return "Houve um erro ao salvar o lançamento."
    
    @staticmethod
    def deletar(db: Session, id: int) -> bool:
        lancamento = db.query(Lancamento).filter(Lancamento.id == id).all()
        if lancamento is not None:
            db.delete(lancamento)
            db.commit()
            return True
        return False