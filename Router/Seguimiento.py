from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Seguimiento import Seguimiento
from Utils.decorator import http_decorator
from Config.db import get_db

seguimiento_router = APIRouter()

@seguimiento_router.post('/buscar_cotizacion', tags=["Seguimiento"], response_model=dict)
@http_decorator
def buscar_cotizacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).buscar_cotizacion(data)
    return response

@seguimiento_router.post('/guardar_seguimiento', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_seguimiento(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_seguimiento(data)
    return response

@seguimiento_router.post('/actualizar_resultado_llamada', tags=["Seguimiento"], response_model=dict)
@http_decorator
def actualizar_resultado_llamada(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).actualizar_resultado_llamada(data)
    return response

@seguimiento_router.post('/guardar_no_adjudicacion', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_no_adjudicacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_no_adjudicacion(data)
    return response

@seguimiento_router.post('/guardar_en_estudio', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_en_estudio(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_en_estudio(data)
    return response

@seguimiento_router.post('/guardar_no_contesta', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_no_contesta(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_no_contesta(data)
    return response

@seguimiento_router.post('/guardar_llamar_mas_tarde', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_llamar_mas_tarde(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_llamar_mas_tarde(data)
    return response

@seguimiento_router.post('/guardar_reprogramar_llamada', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_reprogramar_llamada(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_reprogramar_llamada(data)
    return response

@seguimiento_router.post('/guardar_no_confirmado', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_no_confirmado(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_no_confirmado(data)
    return response

@seguimiento_router.post('/guardar_presentado_plataforma', tags=["Seguimiento"], response_model=dict)
@http_decorator
def guardar_presentado_plataforma(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Seguimiento(db).guardar_presentado_plataforma(data)
    return response
