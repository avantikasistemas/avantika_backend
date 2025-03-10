from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime, timedelta, timezone
import pytz
from Utils.constants import (
    START_WORK_HOUR, END_WORK_HOUR
)

class Cotizacion:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)
        self.holidays = {
            "2025-03-03", "2025-03-04",
            "2025-03-24", "2025-04-17", "2025-04-18", "2025-05-01", 
            "2025-06-02", "2025-06-23", "2025-06-30", "2025-07-20", 
            "2025-08-07", "2025-08-18", "2025-10-13", "2025-11-03", 
            "2025-11-17", "2025-12-08", "2025-12-25"
        }

    def get_tercero_x_nit(self, data: dict):
        """ Api que realiza la consulta del tercero a la base de datos. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        nit = data["nit"].strip()
        fecha = data.get("fecha", None)

        try:
            # Acá usamos la query para traer la información
            datos = self.querys.get_tercero_x_nit(nit)

            # Calculamos fecha de vencimiento
            fecha_venc = self.calculate_expiry_date(datos, fecha)

            # Agregamos la fecha al json de salida
            datos.update({"fecha_vencimiento": fecha_venc})

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", datos)

        except Exception as e:
            print(f"Error al obtener información de tercero: {e}")
            raise CustomException("Error al obtener información de tercero.")

    def calculate_expiry_date(self, datos: dict, fecha: any):

        # Retornamos vacío si no hay fecha ni tipo de cliente
        if not fecha or not datos["tipo_cliente"]:
            return ""

        # Convertimos en mayúscula el tipo de cliente
        tipo_cliente = datos["tipo_cliente"].upper()

        # Calculamos los dias adicionales dependiendo del tipo de cliente
        dias_adicionales = 5 if tipo_cliente in [
            "PUBLICO", "ESAL_PUBLICO"] else 2

        # Obtenemos la fecha de vencimiento
        expiry_date = self.add_business_days(fecha, dias_adicionales)

        # Convertimos la fecha en string
        expiry_date_field = expiry_date.strftime("%d-%m-%Y %H:%M:%S")

        # Retornamos la fecha de vencimiento.
        return expiry_date_field

    def add_business_days(self, start_date, days_to_add):

        fecha_obj = start_date
        current_date = datetime.strptime(fecha_obj, "%d-%m-%Y %H:%M:%S")

        # Si la hora de inicio está fuera del horario laboral, comenzar al siguiente día hábil
        if current_date.time() < START_WORK_HOUR or current_date.time() > END_WORK_HOUR:
            current_date = self.move_to_next_business_day(current_date)

        # Contador de días hábiles agregados
        added_days = 0
        while added_days < days_to_add:
            # Avanza un día
            current_date += timedelta(days=1)
            # Verifica si es un día hábil
            if self.is_business_day(current_date):
                added_days += 1

        # Asegura que la fecha final esté dentro del horario laboral
        if current_date.time() > END_WORK_HOUR:
            current_date = datetime.combine(current_date.date(), START_WORK_HOUR)
        return current_date

    def is_business_day(self, date):
        # Verifica que no sea sábado, domingo ni un día festivo
        return date.weekday() < 5 and date.strftime("%Y-%m-%d") not in self.holidays

    def move_to_next_business_day(self, date):
        # Pasa al próximo día hábil si el día actual es fuera de horario o no hábil
        while not self.is_business_day(date) or date.time() > END_WORK_HOUR:
            date += timedelta(days=1)
            date = datetime.combine(date, START_WORK_HOUR)
        return date

    def calculate_opportunity(self, fecha_entrega, fecha_vencimiento):
        # Convertimos la fecha de vencimiento en tipo datetime para calcular 
        fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y %H:%M:%S")
        # Restamos la fecha de entrega menos vencimiento
        diff = fecha_entrega - fecha_vencimiento
        # Retornamos la diferencia
        return diff
 
    def calculate_delivery_days(self, fecha_entrega, fecha_hora_correo):
        # Convertimos la fecha del registro elegido en tipo datetime para calcular
        fecha_entrada = datetime.strptime(fecha_hora_correo, "%d-%m-%Y %H:%M:%S")
        fecha_entrada = fecha_entrada.astimezone(
            pytz.timezone('America/Bogota')).replace(tzinfo=None)
        # Restamos la fecha de entrega menos vencimiento
        diff = fecha_entrega - fecha_entrada
        # Retornamos la diferencia
        return diff
    
    def consultar_cotizacion(self, data: dict):
        
        # Asignamos los datos de entrada a variables 
        num_cot = data["numero_cotizacion"].strip()
        fecha_hora_correo = data.get("fecha", None)
        fecha_vencimiento = data.get("fecha_vencimiento", None)

        # Inicializamos otras variables
        dias_oportunidad = ""
        dias_entrega = ""
        response = dict()

        try:
            # Acá usamos la query para traer la información
            datos = self.querys.consultar_cotizacion(num_cot)

            if datos:
                fecha_entrega = datos[0]["fecha_hora_entrega"]

                # Calcular la oportunidad en la entrega
                if fecha_vencimiento:
                    diff_dias_oportunidad = self.calculate_opportunity(fecha_entrega, fecha_vencimiento)
                    dias_oportunidad = diff_dias_oportunidad.days

                # Calcular los días de entrega
                if fecha_hora_correo:
                    diff_dias_entrega = self.calculate_delivery_days(fecha_entrega, fecha_hora_correo)
                    dias_entrega = diff_dias_entrega.days

            # Obtenemos el seguimiento
            seguimiento = self.querys.search_seguimiento(num_cot)

            # Armamos el JSON de respuesta
            response = {
                "cotizacion": datos,
                "informacion_extra": {
                    "dias_oportunidad": dias_oportunidad,
                    "dias_entrega": dias_entrega,
                    "seguimiento": seguimiento,
                },
            }

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", response)

        except Exception as e:
            print(f"Error al obtener información de cotización: {e}")
            raise CustomException("Error al obtener información de cotización.")

    def guardar_cotizacion(self, data: dict):

        # Iniciamos un diccionario vacio que será donde se guardara la información.
        data_insert = dict()

        # Asignamos los formatos de fecha deseados
        normal_format = "%d-%m-%Y %H:%M:%S"
        output_format = "%Y-%m-%d %H:%M:%S"

        # Asignamos toda la información entrante a sus respectivas variables
        email_sender = data.get("email_sender", "")
        email_subject = data.get("email_subject", "")
        email_datetime = data.get("email_datetime", "")
        if email_datetime:
            email_datetime = self.tools.format_date(email_datetime, normal_format, output_format)
            email_datetime = datetime.strptime(email_datetime, '%Y-%m-%d %H:%M:%S')
        nit = data.get("nit", "")
        nombre = data.get("nombre", "")
        coordinador = data.get("coordinador", "")
        ejecutivo = data.get("ejecutivo", "")
        tipo_cliente = data.get("tipo_cliente", "")
        zona = data.get("zona", "")
        fecha_vencimiento = data.get("fecha_vencimiento", None)
        if fecha_vencimiento:
            fecha_vencimiento = self.tools.format_date(fecha_vencimiento, normal_format, output_format)
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d %H:%M:%S')
        nueva_fecha_vencimiento = data.get("nueva_fecha_vencimiento", None)
        items_a_cotizar = data.get("items_a_cotizar", "")
        numero_cotizacion = data.get("numero_cotizacion", "")
        cotizacion_concepto = data.get("cotizacion_concepto", "")
        estado = data.get("estado", "")
        fecha_entrega = data.get("fecha_entrega", None)
        if fecha_entrega:
            fecha_entrega = self.tools.format_date(fecha_entrega, '%d-%m-%Y', '%Y-%m-%d')
            fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d')
        usuario_creador_cotizacion = data.get("usuario_creador_cotizacion", "")
        pesos_cotizados = data.get("pesos_cotizados", None)
        if pesos_cotizados:
            pesos_cotizados = self.tools.format_money(pesos_cotizados)
        items_cotizados = data.get("items_cotizados", "")
        oportunidad_entrega = data.get("oportunidad_entrega", "")
        dias_entrega = data.get("dias_entrega", "")
        motivo_no_cotizacion = data.get("motivo_no_cotizacion", "")
        desvio_oportunidad = data.get("desvio_oportunidad", "")
        item_revisado_cumple = data.get("item_revisado_cumple", 0)
        item_revisado_muestra = data.get("item_revisado_muestra", 0)
        porcentaje_muestra = data.get("porcentaje_muestra", 0)
        desvio_calidad = data.get("desvio_calidad", "")

        # Validamos que no venga ni el correo, ni asunto ni fecha y hora vacias.
        if not email_sender or not email_subject or not email_datetime:
            raise CustomException("Error al guardar los datos en la base de datos.")
        
        # Consultamos si existe cotización.
        cotizacion = self.querys.buscar_cotizacion(
            email_sender,
            email_subject,
            email_datetime
        )

        # Armamos el JSON de guardado
        data_insert = {
            "email_sender": email_sender,
            "email_subject": email_subject,
            "email_datetime": email_datetime,
            "nit": nit if nit else '',
            "nombre": nombre if nombre else '',
            "coordinador": coordinador if coordinador else '',
            "ejecutivo": ejecutivo if ejecutivo else '',
            "tipo_cliente": tipo_cliente if tipo_cliente else '',
            "zona": zona if zona else '',
            "fecha_vencimiento": fecha_vencimiento if fecha_vencimiento else None,
            "items_a_cotizar": items_a_cotizar if items_a_cotizar else '',
            "numero_cotizacion": numero_cotizacion if numero_cotizacion else '',
            "cotizacion_concepto": cotizacion_concepto if cotizacion_concepto else '',
            "estado": estado,
            "fecha_entrega": fecha_entrega if fecha_entrega else None,
            "usuario_creador_cotizacion": usuario_creador_cotizacion if usuario_creador_cotizacion else '',
            "pesos_cotizados": pesos_cotizados if pesos_cotizados else None,
            "items_cotizados": items_cotizados if items_cotizados else '',
            "oportunidad_entrega": oportunidad_entrega if oportunidad_entrega else '',
            "dias_entrega": dias_entrega if dias_entrega else '',
            "nueva_fecha_vencimiento": nueva_fecha_vencimiento if nueva_fecha_vencimiento else None,
            "motivo_no_cotizacion": motivo_no_cotizacion.strip() if motivo_no_cotizacion else '',
            "desvio_oportunidad": desvio_oportunidad.strip() if desvio_oportunidad else '',
            "item_revisado_cumple": item_revisado_cumple,
            "item_revisado_muestra": item_revisado_muestra,
            "porcentaje_muestra": porcentaje_muestra,
            "desvio_calidad": desvio_calidad.strip() if desvio_calidad else '',
        }

        # Validamos si existe, si no existe guardamos.
        if cotizacion:
            msg = "Ya existe un registro con esta información. ¿Desea guardar de todos modos?"
            return self.tools.output(210, msg)
        else:
            self.querys.insert_datos_coti(data_insert)

            return self.tools.output(200, "Datos guardados exitosamente en la base de datos.")

    def actualizar_cotizacion(self, data: dict):

        # Iniciamos un diccionario vacio que será donde se guardara la información.
        data_update = dict()
        data_valores_filtro = dict()

        # Asignamos los formatos de fecha deseados
        normal_format = "%d-%m-%Y %H:%M:%S"
        output_format = "%Y-%m-%d %H:%M:%S"

        # Asignamos toda la información entrante a sus respectivas variables
        email_sender = data.get("email_sender", "")
        email_subject = data.get("email_subject", "")
        email_datetime = data.get("email_datetime", "")
        if email_datetime:
            email_datetime = self.tools.format_date(email_datetime, normal_format, output_format)
            email_datetime = datetime.strptime(email_datetime, '%Y-%m-%d %H:%M:%S')
        nit = data.get("nit", "")
        nombre = data.get("nombre", "")
        coordinador = data.get("coordinador", "")
        ejecutivo = data.get("ejecutivo", "")
        tipo_cliente = data.get("tipo_cliente", "")
        zona = data.get("zona", "")
        fecha_vencimiento = data.get("fecha_vencimiento", None)
        if fecha_vencimiento:
            fecha_vencimiento = self.tools.format_date(fecha_vencimiento, normal_format, output_format)
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d %H:%M:%S')
        nueva_fecha_vencimiento = data.get("nueva_fecha_vencimiento", None)
        items_a_cotizar = data.get("items_a_cotizar", "")
        numero_cotizacion = data.get("numero_cotizacion", "")
        cotizacion_concepto = data.get("cotizacion_concepto", "")
        estado = data.get("estado", "")
        fecha_entrega = data.get("fecha_entrega", None)
        if fecha_entrega:
            fecha_entrega = self.tools.format_date(fecha_entrega, '%d-%m-%Y', '%Y-%m-%d')
            fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d')
        usuario_creador_cotizacion = data.get("usuario_creador_cotizacion", "")
        pesos_cotizados = data.get("pesos_cotizados", None)
        if pesos_cotizados:
            pesos_cotizados = self.tools.format_money(pesos_cotizados)
        items_cotizados = data.get("items_cotizados", "")
        oportunidad_entrega = data.get("oportunidad_entrega", "")
        dias_entrega = data.get("dias_entrega", "")
        motivo_no_cotizacion = data.get("motivo_no_cotizacion", "")
        desvio_oportunidad = data.get("desvio_oportunidad", "")
        item_revisado_cumple = data.get("item_revisado_cumple", 0)
        item_revisado_muestra = data.get("item_revisado_muestra", 0)
        porcentaje_muestra = data.get("porcentaje_muestra", 0)
        desvio_calidad = data.get("desvio_calidad", "")

        # Validamos que no venga ni el correo, ni asunto ni fecha y hora vacias.
        if not email_sender or not email_subject or not email_datetime:
            raise CustomException("Error al guardar los datos en la base de datos.")

        # Armamos el JSON de guardado
        data_update = {
            "nit": nit if nit else '',
            "nombre": nombre if nombre else '',
            "coordinador": coordinador if coordinador else '',
            "ejecutivo": ejecutivo if ejecutivo else '',
            "tipo_cliente": tipo_cliente if tipo_cliente else '',
            "zona": zona if zona else '',
            "items_a_cotizar": items_a_cotizar if items_a_cotizar else '',
            "numero_cotizacion": numero_cotizacion if numero_cotizacion else '',
            "cotizacion_concepto": cotizacion_concepto if cotizacion_concepto else '',
            "estado": estado if estado else '',
            "fecha_entrega": fecha_entrega if fecha_entrega else None,
            "usuario_creador_cotizacion": usuario_creador_cotizacion if usuario_creador_cotizacion else '',
            "pesos_cotizados": pesos_cotizados if pesos_cotizados else None,
            "items_cotizados": items_cotizados if items_cotizados else '',
            "oportunidad_entrega": oportunidad_entrega if oportunidad_entrega else '',
            "dias_entrega": dias_entrega if dias_entrega else '',
            "nueva_fecha_vencimiento": nueva_fecha_vencimiento if nueva_fecha_vencimiento else None,
            "motivo_no_cotizacion": motivo_no_cotizacion.strip() if motivo_no_cotizacion else '',
            "desvio_oportunidad": desvio_oportunidad.strip() if desvio_oportunidad else '',
            "item_revisado_cumple": item_revisado_cumple,
            "item_revisado_muestra": item_revisado_muestra,
            "porcentaje_muestra": porcentaje_muestra,
            "desvio_calidad": desvio_calidad.strip() if desvio_calidad else '',
        }

        data_valores_filtro = {
            "email_sender": email_sender,
            "email_subject": email_subject,
            "email_datetime": email_datetime,
            "fecha_vencimiento": fecha_vencimiento
        }

        self.querys.update_datos_coti(data_update, data_valores_filtro)

        return self.tools.output(200, "Registro actualizado exitosamente.")

    def cargar_datos_cotizacion(self, data: dict):

        # Iniciamos diccionario vacío,
        response = dict()

        # Asignamos los formatos de fecha deseados
        normal_format = "%d-%m-%Y %H:%M:%S"
        output_format = "%Y-%m-%d %H:%M:%S"

        # Asignamos toda la información entrante a sus respectivas variables
        email_sender = data.get("email_sender", "")
        email_subject = data.get("email_subject", "")
        email_datetime = data.get("email_datetime", "")
        if email_datetime:
            email_datetime = self.tools.format_date(email_datetime, normal_format, output_format)
            email_datetime = datetime.strptime(email_datetime, '%Y-%m-%d %H:%M:%S')

        # Validamos que no venga ni el correo, ni asunto ni fecha y hora vacias.
        if not email_sender or not email_subject or not email_datetime:
            raise CustomException("Seleccione un correo para comprobar su estado.")
        
        # Consultamos si existe cotización.
        cotizacion = self.querys.buscar_cotizacion(
            email_sender,
            email_subject,
            email_datetime
        )

        # Validamos si no existe la cotización.
        if not cotizacion:
            msg = "No se encontró un registro de seguimiento para el correo seleccionado."
            raise CustomException(msg)
        
        response = {
            "nit": cotizacion.nit,
            "nombre": cotizacion.nombre,
            "coordinador": cotizacion.coordinador,
            "ejecutivo": cotizacion.ejecutivo,
            "tipo_cliente": cotizacion.tipo_cliente,
            "zona": cotizacion.zona,
            "estado": cotizacion.estado,
            "fecha_vencimiento": datetime.strptime(str(cotizacion.fecha_vencimiento), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S") if cotizacion.fecha_vencimiento else '',
            "items_a_cotizar": cotizacion.items_a_cotizar,
            "numero_cotizacion": cotizacion.numero_cotizacion,
            "nueva_fecha_vencimiento": datetime.strptime(str(cotizacion.nueva_fecha_vencimiento), "%Y-%m-%d").strftime("%Y-%m-%d") if cotizacion.nueva_fecha_vencimiento else '',
            "motivo_no_cotizacion": cotizacion.motivo_no_cotizacion,
            "desvio_oportunidad": cotizacion.desvio_oportunidad,
            "item_revisado_cumple": cotizacion.item_revisado_cumple,
            "item_revisado_muestra": cotizacion.item_revisado_muestra,
            "porcentaje_muestra": cotizacion.porcentaje_muestra,
            "desvio_calidad": cotizacion.desvio_calidad,
        }

        # Retornamos la respuesta
        return self.tools.output(200, "Datos cargados correctamente desde el seguimiento.", response)
