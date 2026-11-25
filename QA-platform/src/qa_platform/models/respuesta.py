from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.models.publicacion import Publicacion

if TYPE_CHECKING:
    # Solo para anotaciones: pregunta.py importa a este módulo, y así se evita
    # un import circular. Autor tampoco se importa: Respuesta no debe depender
    # del tipo concreto de autor (Usuario o IA).
    from qa_platform.models.autor import Autor
    from qa_platform.models.pregunta import Pregunta


def _es_texto_valido(valor) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


class Respuesta(Publicacion):
    """Respuesta a una Pregunta, escrita por un Autor (Usuario o IA).

    Pertenece a UNA sola pregunta (una pregunta tiene 0..* respuestas) y tiene
    un autor. Nace sin aceptar (esAceptada = False) y la fecha la fija el
    sistema al crearla. Si los datos no son válidos, no se crea y se lanza
    ErrorValidacion con TODOS los errores encontrados.

    Normalmente no se instancia a mano: se crea con Autor.crearRespuesta(),
    que además la registra en la pregunta.
    """

    def __init__(
        self,
        cuerpo: str,
        pregunta: Pregunta,
        autor: Autor,
        fecha: datetime | None = None,
    ):
        errores: dict[str, str] = {}
        if not _es_texto_valido(cuerpo):
            errores["cuerpo"] = "El cuerpo es obligatorio"
        if pregunta is None:
            errores["pregunta"] = "La respuesta debe pertenecer a una pregunta"
        if autor is None:
            errores["autor"] = "La respuesta debe tener un autor"
        if errores:
            raise ErrorValidacion(errores)

        super().__init__(cuerpo.strip(), fecha)
        self.esAceptada: bool = False
        self.pregunta = pregunta
        self.autor = autor

    def __repr__(self):
        return f"<Respuesta de {self.autor!r} a {self.pregunta!r}>"