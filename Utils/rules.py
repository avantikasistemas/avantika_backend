from .validator import Validator


class Rules:
    """ Esta clase se encarga de validar los datos de entrada de la API
        y si hay un error, lanza una excepcion """

    val = Validator()

    def __init__(self, path: str, params: dict):
        path_dict = {
            "/get_emails": self.__val_get_emails,
        }
        # Se obtiene la funcion a ejecutar
        func = path_dict.get(path, None)
        if func:
            # Se ejecuta la funcion para obtener las reglas de validacion
            validacion_dict = func(params)

            # Se valida la datas
            self.val.validacion_datos_entrada(validacion_dict)

    def __val_get_emails(self, params):
        validacion_dict = [
            {
                "tipo": "date",
                "campo": "fecha de inicio",
                "valor": params["start_date"],
                "obligatorio": False,
            },
            {
                "tipo": "date",
                "campo": "fecha fin",
                "valor": params["end_date"],
                "obligatorio": False,
            }
        ]
        return validacion_dict
