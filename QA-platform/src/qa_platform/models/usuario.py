from collections.abc import Iterable
from datetime import datetime

from qa_platform.extensions import db
from qa_platform.models.autor import Autor
from qa_platform.models.categoria import Categoria
from qa_platform.models.enums import RolUsuario
from qa_platform.models.etiqueta import Etiqueta
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

    def generarPregunta(
        self,
        titulo: str,
        cuerpo: str,
        fecha: datetime | None = None,
        *,
        categoria: Categoria,
        etiquetas: Iterable[Etiqueta] = (),
    ) -> Pregunta:
        """Crea y devuelve una Pregunta cuyo autor es este usuario.

        Los tres primeros parámetros son los del diagrama. La categoría y las
        etiquetas se agregan con nombre porque el issue pide asociarlas.
        Si no se indica la fecha, se usa el momento actual.

        Lanza ErrorValidacion si falta el título, el cuerpo o la categoría.
        Este método no guarda la pregunta en ningún lado: de eso se ocupa
        el servicio.
        """
        return Pregunta(
            titulo=titulo,
            cuerpo=cuerpo,
            categoria=categoria,
            autor=self,
            etiquetas=etiquetas,
            fecha=fecha,
        )

    def __repr__(self):
        return f"<Usuario {self.correo}>"