"""Modelos del dominio.

Cada issue del diagrama agrega su módulo acá (autor.py, usuario.py,
publicacion.py, etc.) y lo exporta en este archivo.
"""

from qa_platform.models.enums import RolUsuario, TipoVoto

__all__ = ["RolUsuario", "TipoVoto"]