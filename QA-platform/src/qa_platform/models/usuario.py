from __future__ import annotations

from typing import TYPE_CHECKING

from qa_platform.extensions import db
from qa_platform.models.autor import Autor
from qa_platform.models.enums import RolUsuario
from qa_platform.models.respuesta import Respuesta

if TYPE_CHECKING:
    # Solo para anotaciones de tipo.
    from qa_platform.models.pregunta import Pregunta


class Usuario(Autor):
    """Usuario humano registrado en la plataforma."""

    __tablename__ = "usuario"

    # Clave primaria y a la vez clave foránea hacia la tabla padre.
    identificacion = db.Column(
        db.Integer,
        db.ForeignKey("autor.identificacion"),
        primary_key=True,
    )
    # Guardará el HASH de la contraseña, nunca el texto plano (issue #4).
    password = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=False, unique=True)
    rol = db.Column(
        db.Enum(RolUsuario),
        nullable=False,
        default=RolUsuario.USUARIO_GENERAL,
    )

    __mapper_args__ = {"polymorphic_identity": "usuario"}

    def crearRespuesta(self, p: Pregunta, cuerpo: str) -> Respuesta:
        """Crea una respuesta de este usuario a la pregunta p y la registra en ella.

        Sobrescribe el método abstracto de Autor. Quien lo llama no necesita
        saber qué tipo de Autor es: cada subclase define cómo responde.
        """
        respuesta = Respuesta(cuerpo, pregunta=p, autor=self)
        p.agregar_respuesta(respuesta)
        return respuesta

    def __repr__(self):
        return f"<Usuario {self.correo}>"