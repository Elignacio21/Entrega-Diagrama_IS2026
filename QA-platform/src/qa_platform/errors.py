class ErrorValidacion(Exception):
    """Los datos recibidos no cumplen las reglas del dominio.

    Lleva un diccionario {campo: mensaje} para poder informar todos los
    errores juntos (correo inválido, campo vacío, correo repetido, etc.).
    """

    def __init__(self, errores: dict[str, str]):
        super().__init__("; ".join(errores.values()))
        self.errores = errores

class ErrorNoEncontrado(Exception):
    """Un recurso pedido por su identificador no existe (por ejemplo, una pregunta)."""

    def __init__(self, errores: dict[str, str]):
        super().__init__("; ".join(errores.values()))
        self.errores = errores