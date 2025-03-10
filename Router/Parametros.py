from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Parametros import Parametros
from Utils.decorator import http_decorator
from Config.db import get_db

parametros_router = APIRouter()

@parametros_router.post('/get_tipos_estado', tags=["Parametros"], response_model=dict)
@http_decorator
def get_tipos_estado(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).get_tipos_estado()
    return response
