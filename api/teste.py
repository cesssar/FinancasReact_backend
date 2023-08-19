from classes.database import *
from classes.models import *
from classes.crud import *

session = SessionLocal()

print(session.query(func.sum(Conta.saldo)).filter_by(id_usuario=1).all()[0][0])


