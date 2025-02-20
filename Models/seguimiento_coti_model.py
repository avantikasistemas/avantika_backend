from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Text, Integer, DateTime, DECIMAL, Date

class SeguimientoCotiModel(BASE):

    __tablename__= "seguimiento_coti"
    
    id = Column(BigInteger, primary_key=True)
    email_sender = Column(String, nullable=False)
    email_subject = Column(String, nullable=True)
    email_datetime = Column(DateTime(), nullable=True)
    nit = Column(String, nullable=True)
    nombre = Column(String, nullable=False)
    coordinador = Column(String, nullable=True)
    ejecutivo = Column(String, nullable=False)
    tipo_cliente = Column(String, nullable=True)
    zona = Column(String, nullable=True)
    fecha_vencimiento = Column(DateTime(), nullable=True)
    numero_cotizacion = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    cotizacion_concepto = Column(String, nullable=True)
    fecha_entrega = Column(DateTime(), nullable=True)
    usuario_creador_cotizacion = Column(String, nullable=True)
    pesos_cotizados = Column(DECIMAL, nullable=True)
    items_cotizados = Column(Integer, nullable=True)
    oportunidad_entrega = Column(String, nullable=True)
    dias_entrega = Column(Integer, nullable=True)
    items_a_cotizar = Column(String, nullable=True)
    seguimiento_usuario = Column(String, nullable=True)
    seguimiento_actividad = Column(String, nullable=True)
    seguimiento_resultado = Column(String, nullable=True)
    seguimiento_comentario = Column(Text)
    seguimiento_fecha_creacion = Column(DateTime(), nullable=True)
    nueva_fecha_vencimiento = Column(Date, nullable=True)
    
    # def __init__(self, data: dict):
    #     self.type_document = data['type_document']
    #     self.document = data['document']
    #     self.first_name = data['first_name']
    #     self.second_name = data['second_name']
    #     self.last_name = data['last_name']
    #     self.second_last_name = data['second_last_name']
    #     self.full_name = data['full_name']
    #     self.email = data['email']
    #     self.password = data['password']
    #     self.user_type_id = data['user_type_id']
    