from __future__ import annotations

from typing import TYPE_CHECKING

from qa_platform.extensions import db

if TYPE_CHECKING:
    # Solo para anotaciones de tipo; estas clases se crean en los issues #5 y #7.
    from qa_platform.models.pregunta import Pregunta
    from qa_platform.models.respuesta import Respuesta


class Autor(db.Model):
    """Abstracción de quién escribe una respuesta (Usuario o IA).

    Es abstracta: solo existe para que Usuario e IA compartan una base común.
    Se mapea con herencia de tabla unida (joined table inheritance): esta tabla
    guarda lo común y cada subclase tiene su propia tabla con lo específico.
    """

    __tablename__ = "autor"

    identificacion = db.Column(db.Integer, primary_key=True)
    # Columna discriminadora: indica a qué subclase corresponde cada fila.
    tipo = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {"polymorphic_on": "tipo"}

    def crearRespuesta(self, p: Pregunta, cuerpo: str) -> Respuesta:
        """Método abstracto: cada subclase define cómo crea su respuesta."""
        raise NotImplementedError(
            f"{type(self).__name__} debe implementar crearRespuesta()"
        )