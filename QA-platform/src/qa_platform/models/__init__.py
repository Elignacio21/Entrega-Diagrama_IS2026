"""Importar todos los modelos acá garantiza que SQLAlchemy los conozca.

Alembic autogenera las migraciones a partir de db.metadata, y las relaciones
escritas como texto (por ejemplo "Respuesta") solo se resuelven si la clase
ya fue importada. Este archivo NO debe definir clases: solo re-exportarlas.
"""

from qa_platform.models.autor import Autor
from qa_platform.models.categoria import Categoria
from qa_platform.models.enums import RolUsuario, TipoVoto
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.publicacion import Publicacion
from qa_platform.models.pregunta import Pregunta
from qa_platform.models.respuesta import Respuesta
from qa_platform.models.voto import Voto
from qa_platform.models.usuario import Usuario
from qa_platform.models.ia import IA

__all__ = [
    "Autor",
    "Categoria",
    "Etiqueta",
    "IA",
    "Pregunta",
    "Publicacion",
    "Respuesta",
    "RolUsuario",
    "TipoVoto",
    "Usuario",
    "Voto",
]