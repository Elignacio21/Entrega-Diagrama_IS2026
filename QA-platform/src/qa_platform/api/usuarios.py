from flask import Blueprint, request

from qa_platform.errors import ErrorValidacion
from qa_platform.services.usuario_service import listar_usuarios, registrar_usuario

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@usuarios_bp.post("")
def crear_usuario():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    try:
        usuario = registrar_usuario(
            correo=datos.get("correo"),
            password=datos.get("password"),
        )
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return {
        "identificacion": usuario.identificacion,
        "correo": usuario.correo,
        "rol": usuario.rol.name,
    }, 201


@usuarios_bp.get("")
def obtener_usuarios():
    usuarios = listar_usuarios()
    return {
        "total": len(usuarios),
        "usuarios": [
            {
                "identificacion": u.identificacion,
                "correo": u.correo,
                "rol": u.rol.name,
            }
            for u in usuarios
        ],
    }, 200