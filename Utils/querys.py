
from Config.db import session
from Utils.tools import Tools, CustomException
from sqlalchemy import func, and_
from Models.seguimiento_coti_model import SeguimientoCotiModel

class Querys:

    def __init__(self):
        self.tools = Tools()

    # Query para obtener el estado del seguimiento, si no lo tiene se agrega 'sin seguimiento'
    def check_follow_up(self, sender: str, subject: str, received_time: str):

        try:
            query = session.query(
                SeguimientoCotiModel
            ).filter(
                SeguimientoCotiModel.email_sender == sender,
                SeguimientoCotiModel.email_subject == subject,
                SeguimientoCotiModel.email_datetime == received_time
            ).first()                 

            # Devolvemos el estado si la consulta encuentra una fila
            return query.estado if query else "Sin seguimiento"
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()
