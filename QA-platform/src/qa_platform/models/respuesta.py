from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
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

    esAceptada es de solo lectura: la única forma de aceptarla es
    marcarAceptada() (o Usuario.aceptarRespuesta(), que valida quién acepta).

    Normalmente no se instancia a mano: se crea con Autor.crearRespuesta(),
    que además la registra en la pregunta.
    """

    __tablename__ = "respuesta"

    identificacion = db.Column(
        db.Integer,
        db.ForeignKey("publicacion.identificacion"),
        primary_key=True,
    )
    pregunta_id = db.Column(
        db.Integer, db.ForeignKey("pregunta.identificacion"), nullable=False
    )
    # Apunta a `autor` (la tabla base) y no a `usuario`: así sirve para
    # respuestas escritas tanto por un Usuario como por una IA.
    autor_id = db.Column(
        db.Integer, db.ForeignKey("autor.identificacion"), nullable=False
    )
    # La columna se llama es_aceptada en la base; en Python se lee con la
    # propiedad esAceptada (solo lectura).
    _esAceptada = db.Column("es_aceptada", db.Boolean, nullable=False, default=False)

    pregunta = db.relationship(
        "Pregunta", back_populates="_respuestas", foreign_keys=[pregunta_id]
    )
    autor = db.relationship("Autor", foreign_keys=[autor_id])

    __mapper_args__ = {"polymorphic_identity": "respuesta"}

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
        self._esAceptada = False
        self.pregunta = pregunta
        self.autor = autor
        # Ya NO se hace `self.identificacion = None`: lo asigna la base al guardar.

    @property
    def esAceptada(self) -> bool:
        return self._esAceptada

    def marcarAceptada(self) -> None:
        """Marca esta respuesta como la aceptada de su pregunta.

        Una pregunta tiene como máximo UNA respuesta aceptada: si ya hay otra,
        se lanza ErrorValidacion. Aceptar la que ya estaba aceptada no hace
        nada. Esta regla vive acá (y no solo en Usuario) para que no se pueda
        saltear por ninguna vía.
        """
        aceptada = self.pregunta.respuesta_aceptada
        if aceptada is not None and aceptada is not self:
            raise ErrorValidacion(
                {"respuesta": "La pregunta ya tiene una respuesta aceptada"}
            )
        self._esAceptada = True

    def __repr__(self):
        return f"<Respuesta de {self.autor!r} a {self.pregunta!r}>"