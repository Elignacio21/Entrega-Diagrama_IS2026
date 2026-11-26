from __future__ import annotations

from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.enums import TipoVoto

if TYPE_CHECKING:
    from qa_platform.models.publicacion import Publicacion
    from qa_platform.models.usuario import Usuario


class Voto(db.Model):
    """Voto emitido por un Usuario sobre una Publicacion."""

    __tablename__ = "voto"
    # La regla "un usuario vota una sola vez cada publicación" ahora también
    # la garantiza la base de datos, no solo el código Python.
    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id", "publicacion_id", name="uq_voto_usuario_publicacion"
        ),
    )

    identificacion = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuario.identificacion"), nullable=False
    )
    publicacion_id = db.Column(
        db.Integer, db.ForeignKey("publicacion.identificacion"), nullable=False
    )
    tipo = db.Column(db.Enum(TipoVoto), nullable=False)

    usuario = db.relationship("Usuario")
    publicacion = db.relationship("Publicacion", back_populates="_votos")

    def __init__(self, usuario: Usuario, publicacion: Publicacion, tipo: TipoVoto):
        errores: dict[str, str] = {}
        if usuario is None:
            errores["usuario"] = "El voto debe tener un usuario"
        if publicacion is None:
            errores["publicacion"] = "El voto debe pertenecer a una publicación"
        if not isinstance(tipo, TipoVoto):
            errores["tipo"] = "El tipo de voto debe ser POSITIVO o NEGATIVO"
        if errores:
            raise ErrorValidacion(errores)

        self.usuario = usuario
        self.publicacion = publicacion
        self.tipo = tipo

    def __repr__(self):
        return f"<Voto {self.tipo.value} de {self.usuario!r} en {self.publicacion!r}>"