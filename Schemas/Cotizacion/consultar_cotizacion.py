from pydantic import BaseModel
from typing import Optional

class ConsultarCotizacion(BaseModel):
    numero_cotizacion: str
    nueva_fecha_vencimiento: Optional[str] = None
