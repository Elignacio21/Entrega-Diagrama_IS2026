import re
from itertools import count

from werkzeug.security import generate_password_hash

from qa_platform.errors import ErrorValidacion
from qa_platform.models.enums import RolUsuario
from qa_platform.models.usuario import Usuario

CORREO_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LONGITUD_MINIMA_PASSWORD = 8

_usuarios_en_memoria: list[Usuario] = []
_siguiente_id = count(start=1)


def listar_usuarios() -> list[Usuario]:
    """Devuelve los usuarios guardados en memoria."""
    return list(_usuarios_en_memoria)


def limpiar_usuarios() -> None:
    """Limpia los datos en memoria."""
    _usuarios_en_memoria.clear()


def _validar_registro(correo: str | None, password: str | None) -> dict[str, str]:
    errores: dict[str, str] = {}

    correo_limpio = correo.strip().lower() if isinstance(correo, str) else ""
    if not correo_limpio:
        errores["correo"] = "El correo es obligatorio"
    elif not CORREO_REGEX.match(correo_limpio):
        errores["correo"] = "El correo no tiene un formato válido"
    elif any(usuario.correo == correo_limpio for usuario in _usuarios_en_memoria):
        errores["correo"] = "El correo ya está registrado"

    if not isinstance(password, str) or not password:
        errores["password"] = "La contraseña es obligatoria"
    elif len(password) < LONGITUD_MINIMA_PASSWORD:
        errores["password"] = (
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_PASSWORD} caracteres"
        )

    return errores


def registrar_usuario(correo: str, password: str) -> Usuario:
    """Valida, hashea y registra un usuario en memoria."""
    errores = _validar_registro(correo, password)
    if errores:
        raise ErrorValidacion(errores)

    usuario = Usuario(
        identificacion=next(_siguiente_id),
        correo=correo.strip().lower(),
        password=generate_password_hash(password),
        rol=RolUsuario.USUARIO_GENERAL,
    )
    _usuarios_en_memoria.append(usuario)
    return usuario