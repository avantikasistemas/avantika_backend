from fastapi import APIRouter, Request # Depends
from Schemas.Cotizacion.get_tercero_x_nit import GetTerceroNit
from Schemas.Cotizacion.consultar_cotizacion import ConsultarCotizacion
from Class.Cotizacion import Cotizacion
from Utils.decorator import http_decorator

cotizacion_router = APIRouter()

@cotizacion_router.post('/get_tercero_x_nit', tags=["Cotización"], response_model=dict)
@http_decorator
def get_tercero_x_nit(request: Request, getTerceroNit: GetTerceroNit):
    data = getattr(request.state, "json_data", {})
    response = Cotizacion().get_tercero_x_nit(data)
    return response

@cotizacion_router.post('/consultar_cotizacion', tags=["Cotización"], response_model=dict)
@http_decorator
def consultar_cotizacion(request: Request, consultarCotizacion: ConsultarCotizacion):
    data = getattr(request.state, "json_data", {})
    response = Cotizacion().consultar_cotizacion(data)
    return response

@cotizacion_router.post('/guardar_cotizacion', tags=["Cotización"], response_model=dict)
@http_decorator
def guardar_cotizacion(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Cotizacion().guardar_cotizacion(data)
    return response

@cotizacion_router.post('/actualizar_cotizacion', tags=["Cotización"], response_model=dict)
@http_decorator
def actualizar_cotizacion(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Cotizacion().actualizar_cotizacion(data)
    return response

@cotizacion_router.post('/cargar_datos_cotizacion', tags=["Cotización"], response_model=dict)
@http_decorator
def cargar_datos_cotizacion(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Cotizacion().cargar_datos_cotizacion(data)
    return response
