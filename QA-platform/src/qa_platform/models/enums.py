import enum


class RolUsuario(enum.Enum):
    """Rol de un usuario dentro de la plataforma."""

    ADMIN = "ADMIN"
    USUARIO_GENERAL = "USUARIO_GENERAL"


class TipoVoto(enum.Enum):
    """Sentido de un voto sobre una publicación."""

    POSITIVO = "POSITIVO"
    NEGATIVO = "NEGATIVO"