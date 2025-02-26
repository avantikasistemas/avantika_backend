
from Config.db import session
from Utils.tools import Tools, CustomException
from sqlalchemy import func, and_
from Models.seguimiento_coti_model import SeguimientoCotiModel
from sqlalchemy import text

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
            if query:
                if query.estado == '' or not query.estado:
                    return "Sin seguimiento"
                else:
                    return query.estado
            else:
                return "Sin seguimiento"
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()

    # Query para obtener los datos del tercero por medio del nit
    def get_tercero_x_nit(self, nit: str):

        response = {
            "nit": "No encontrado",
            "nombres": "No encontrado",
            "coordinador": "No encontrado",
            "ejecutivo": "No encontrado",
            "tipo_cliente": "No encontrado",
            "zona": "No encontrado",
        }
        try:
            sql = """
                SELECT t.nit, t.nombres, tv.coordinador, tv.ejecutivo, dbo.terceros_16.descripcion AS 'tipo_cliente', dbo.terceros_2.descripcion AS 'zona'
                FROM   dbo.terceros AS t 
                INNER JOIN dbo.terceros_ventas AS tv ON t.concepto_2 = tv.concepto_2 
                INNER JOIN dbo.terceros_16 ON t.concepto_16 = dbo.terceros_16.concepto_16 
                INNER JOIN dbo.terceros_2 ON t.concepto_2 = dbo.terceros_2.concepto_2
                WHERE t.nit = :nit;
            """

            query = session.execute(text(sql), {"nit": nit}).fetchone()

            if query:
                response.update({
                    "nit": query.nit,
                    "nombres": query.nombres,
                    "coordinador": query.coordinador,
                    "ejecutivo": query.ejecutivo,
                    "tipo_cliente": query.tipo_cliente,
                    "zona": query.zona,
                })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()
    
    # Query para obtener los tipos de estado para la cotizacion
    def get_tipos_estado(self):

        try:
            response = list()
            sql = """
                SELECT * FROM tipo_transacciones_concep2_ped WHERE sw = 2 ORDER BY concepto ASC;
            """

            query = session.execute(text(sql)).fetchall()
            if query:
                for key in query:
                    response.append(key[2])

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()
    
    # Query para obtener los datos de la cotizacion
    def consultar_cotizacion(self, num_cot):

        try:
            response = list()
            sql = """
                SELECT DISTINCT TOP (40000) 
                    t1.descripcion AS descripcion_concep1,
                    t2.descripcion AS descripcion_concep2,
                    dp.fecha_hora_entrega,
                    dp.usuario,
                    -- Cálculo del total ajustado
                    (SELECT SUM(cantidad * valor_unitario) 
                    FROM dbo.documentos_lin_ped dl
                    WHERE dl.numero = dp.numero AND dl.sw = dp.sw) AS Pesos_cotizados,
                    
                    -- Conteo de filas
                    (SELECT COUNT(*)
                    FROM dbo.documentos_lin_ped dl
                    WHERE dl.numero = dp.numero AND dl.sw = dp.sw) AS CantidadFilas
                FROM dbo.documentos_ped dp
                INNER JOIN dbo.tipo_transacciones_concep_ped t1 
                    ON dp.sw = t1.sw AND dp.concepto = t1.concepto
                INNER JOIN dbo.tipo_transacciones_concep2_ped t2 
                    ON dp.concepto2 = t2.concepto
                WHERE dp.numero = :numero AND dp.sw = 2;
            """

            query = session.execute(text(sql), {"numero": num_cot}).fetchall()
            if query:
                for i, key in enumerate(query):
                    fecha_hora_entrega = key.fecha_hora_entrega if key.fecha_hora_entrega else ""
                    fecha_hora_entrega_str = self.tools.format_date2(str(key.fecha_hora_entrega)) if key.fecha_hora_entrega else ""
                    pesos_cotizados = f"{float(key.Pesos_cotizados):,.2f}" if key.Pesos_cotizados else 0
                    response.append({
                        "id": i+1,
                        "descripcion_concep1": key.descripcion_concep1,
                        "descripcion_concep2": key.descripcion_concep2,
                        "fecha_hora_entrega": fecha_hora_entrega,
                        "fecha_hora_entrega_str": fecha_hora_entrega_str,
                        "usuario": key.usuario,
                        "pesos_cotizados": pesos_cotizados,
                        "cantidad_filas": key.CantidadFilas,
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()

    # Query para obtener la información del seguimiento.
    def search_seguimiento(self, num_cot):

        try:
            response = "No tiene seguimiento"
            result = ""
            sql = """
                SELECT des_usuario AS 'Usuario', Desc_actividad AS 'Actividad', Desc_resultado AS 'Resultado_Seguimiento', comentario AS 'Comentario',Fecha_creacion
                FROM Q_Seguimiento_Actividades_CRM
                WHERE documento = :documento;
            """
            query = session.execute(text(sql), {"documento": num_cot}).fetchall()

            if query:
                for key in query:
                    result += f"Usuario: {key.Usuario}\n"
                    result += f"Actividad: {key.Actividad}\n"
                    result += f"Resultado_Seguimiento: {key.Resultado_Seguimiento}\n"
                    result += f"Comentario: {key.Comentario}\n"
                    result += f"Fecha_creacion: {key.Fecha_creacion}\n"
                    result += "-" * 70 + "\n"

                response = result

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()

    # Query para buscar si la cotizacion existe
    def buscar_cotizacion(self, sender: str, subject: str, received_time: str):

        try:
            query = session.query(
                SeguimientoCotiModel
            ).filter(
                SeguimientoCotiModel.email_sender == sender,
                SeguimientoCotiModel.email_subject == subject,
                SeguimientoCotiModel.email_datetime == received_time
            ).first()                 

            # Devolvemos si hay registro
            return query
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            session.close()

    # Query para insertar datos de la cotizacion.
    def insert_datos_coti(self, data: dict):
        try:
            details = SeguimientoCotiModel(data)
            session.add(details)
            session.commit()
        except Exception as ex:
            raise CustomException(str(ex))
        finally:
            session.close()
        return True

    # Query para actualizar los datos de la cotizacion.
    def update_datos_coti(self, data: dict, data_filtros: dict):
        try:
            rows_updated = session.query(
                SeguimientoCotiModel
            ).filter(
                SeguimientoCotiModel.email_sender == data_filtros["email_sender"],
                SeguimientoCotiModel.email_subject == data_filtros["email_subject"],
                SeguimientoCotiModel.email_datetime == data_filtros["email_datetime"]
            ).update(data)                     
            session.commit()
            if rows_updated == 0:
                print("No se encontró ningún registro para actualizar.")
                
        except Exception as ex:
            raise CustomException(str(ex))
        finally:
            session.close()

        return True
