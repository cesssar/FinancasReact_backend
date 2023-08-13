from classes.database import *
from classes.models import *
from classes.crud import *

session = SessionLocal()

print(session.query(Usuario).offset(0).limit(10).all())

print(session.query(Categoria).filter_by(id_usuario=1).all())
exit()


for i in session.query(Categoria).filter_by(id_usuario=1):
    print(i.categoria)

