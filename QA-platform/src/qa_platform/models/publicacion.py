from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.enums import TipoVoto

if TYPE_CHECKING:
    from qa_platform.models.voto import Voto


def _es_texto_valido(valor) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


class Publicacion(db.Model):
    """Clase base para publicaciones votables (Pregunta y Respuesta).

    Herencia de tabla unida, igual que Autor: esta tabla guarda lo común
    (cuerpo, fecha) y Pregunta / Respuesta tienen su propia tabla con lo
    específico. Así un Voto puede apuntar a cualquiera de las dos con una
    sola clave foránea (publicacion_id).
    """

    __tablename__ = "publicacion"

    identificacion = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    cuerpo = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relación con los votos. El guion bajo mantiene el patrón del proyecto:
    # se lee con la propiedad `votos` (tupla) y se escribe con agregar_voto().
    _votos = db.relationship("Voto", back_populates="publicacion")

    __mapper_args__ = {"polymorphic_on": "tipo"}

    def __init__(self, cuerpo: str, fecha: datetime | None = None):
        if not _es_texto_valido(cuerpo):
            raise ErrorValidacion({"cuerpo": "El cuerpo es obligatorio"})

        self.cuerpo = cuerpo.strip()
        self.fecha = fecha if fecha is not None else datetime.now()
        # OJO: acá ya NO se crea `self._votos = []`. Es una relación de
        # SQLAlchemy y la gestiona el ORM (también al cargar desde la base).

    @property
    def votos(self) -> tuple[Voto, ...]:
        return tuple(self._votos)

    def agregar_voto(self, voto: Voto) -> None:
        from qa_platform.models.voto import Voto

        if not isinstance(voto, Voto):
            raise ErrorValidacion({"voto": "Debe ser un Voto"})
        if voto.publicacion is not self:
            raise ErrorValidacion({"voto": "El voto pertenece a otra publicación"})
        # `v is not voto`: al crear Voto(publicacion=self) la relación bidireccional
        # ya lo agregó a esta lista, y no debe contarse contra sí mismo.
        if any(v is not voto and v.usuario is voto.usuario for v in self._votos):
            raise ErrorValidacion({"voto": "El usuario ya votó esta publicación"})
        if voto not in self._votos:
            self._votos.append(voto)

    def calcularPuntuacion(self) -> int:
        """Devuelve votos POSITIVO menos NEGATIVO (0 si no hay votos)."""
        positivos = sum(1 for v in self._votos if v.tipo == TipoVoto.POSITIVO)
        negativos = sum(1 for v in self._votos if v.tipo == TipoVoto.NEGATIVO)
        return positivos - negativos