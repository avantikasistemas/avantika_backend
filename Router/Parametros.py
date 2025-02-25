from fastapi import APIRouter, Request # Depends
from Class.Parametros import Parametros
from Utils.decorator import http_decorator

parametros_router = APIRouter()

@parametros_router.post('/get_tipos_estado', tags=["Parametros"], response_model=dict)
@http_decorator
def get_tipos_estado(request: Request):
    response = Parametros().get_tipos_estado()
    return response
