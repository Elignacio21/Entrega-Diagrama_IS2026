import re

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.enums import RolUsuario
from qa_platform.models.usuario import Usuario

CORREO_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LONGITUD_MINIMA_PASSWORD = 8


def listar_usuarios() -> list[Usuario]:
    """Devuelve los usuarios guardados en la base."""
    return list(db.session.scalars(db.select(Usuario).order_by(Usuario.identificacion)))


def buscar_usuario(usuario_id) -> Usuario | None:
    """Busca un usuario por su identificacion; None si no existe."""
    # bool es un subtipo de int en Python: True == 1, y no debe valer como id.
    if isinstance(usuario_id, bool) or not isinstance(usuario_id, int):
        return None
    return db.session.get(Usuario, usuario_id)


def limpiar_usuarios() -> None:
    """Se mantiene solo para no romper tests viejos.

    Con base de datos el aislamiento lo hace conftest.py (create_all/drop_all
    por test). Cuando ya no se la llame desde ningún test, se puede borrar.
    """


def _correo_registrado(correo: str) -> bool:
    return db.session.scalar(db.select(Usuario).where(Usuario.correo == correo)) is not None


def _validar_registro(correo: str | None, password: str | None) -> dict[str, str]:
    errores: dict[str, str] = {}

    correo_limpio = correo.strip().lower() if isinstance(correo, str) else ""
    if not correo_limpio:
        errores["correo"] = "El correo es obligatorio"
    elif not CORREO_REGEX.match(correo_limpio):
        errores["correo"] = "El correo no tiene un formato válido"
    elif _correo_registrado(correo_limpio):
        errores["correo"] = "El correo ya está registrado"

    if not isinstance(password, str) or not password:
        errores["password"] = "La contraseña es obligatoria"
    elif len(password) < LONGITUD_MINIMA_PASSWORD:
        errores["password"] = (
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_PASSWORD} caracteres"
        )

    return errores


def registrar_usuario(correo: str, password: str) -> Usuario:
    """Valida, hashea y guarda un usuario en la base."""
    errores = _validar_registro(correo, password)
    if errores:
        raise ErrorValidacion(errores)

    usuario = Usuario(
        correo=correo.strip().lower(),
        password=generate_password_hash(password),
        rol=RolUsuario.USUARIO_GENERAL,
    )
    db.session.add(usuario)
    try:
        db.session.commit()
    except IntegrityError:
        # Dos registros simultáneos con el mismo correo: la restricción UNIQUE
        # de la base es la última defensa (el chequeo de arriba no alcanza).
        db.session.rollback()
        raise ErrorValidacion({"correo": "El correo ya está registrado"}) from None
    return usuario