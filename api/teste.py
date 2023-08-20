from classes.database import *
from sqlalchemy.orm import Session
from fastapi import Depends
from classes.models import *
from sqlalchemy import extract 
from datetime import datetime

from fastapi.encoders import jsonable_encoder

lista = [
    {
        "data": "19/08/2023",
        "texto": "novo texto"
    },
    {
        "data": "19/08/2023",
        "texto": "novo texto"
    }
]

p = jsonable_encoder(lista)

print(p)