from flask import Blueprint, request

from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.services.respuesta_service import (
    aceptar_respuesta,
    crear_respuesta,
    listar_respuestas,
)

respuestas_bp = Blueprint(
    "respuestas", __name__, url_prefix="/api/preguntas/<int:pregunta_id>/respuestas"
)


def _a_diccionario(respuesta) -> dict:
    return {
        "identificacion": respuesta.identificacion,
        "cuerpo": respuesta.cuerpo,
        "fecha": respuesta.fecha.isoformat(),
        "esAceptada": respuesta.esAceptada,
        "autor_id": respuesta.autor.identificacion,
        "pregunta_id": respuesta.pregunta.identificacion,
        "puntuacion": respuesta.calcularPuntuacion(),
    }


@respuestas_bp.post("")
def registrar_respuesta(pregunta_id):
    """Adaptador HTTP: traduce JSON <-> dominio. Las reglas viven en el modelo."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    # La fecha y esAceptada no se leen del cliente: los fija el sistema.
    try:
        respuesta = crear_respuesta(
            pregunta_id=pregunta_id,
            autor_id=datos.get("autor_id"),
            cuerpo=datos.get("cuerpo"),
        )
    except ErrorNoEncontrado as error:
        return {"errores": error.errores}, 404
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return _a_diccionario(respuesta), 201


@respuestas_bp.get("")
def obtener_respuestas(pregunta_id):
    try:
        respuestas = listar_respuestas(pregunta_id)
    except ErrorNoEncontrado as error:
        return {"errores": error.errores}, 404

    return {
        "total": len(respuestas),
        "respuestas": [_a_diccionario(respuesta) for respuesta in respuestas],
    }, 200


@respuestas_bp.post("/<int:respuesta_id>/aceptar")
def marcar_respuesta_aceptada(pregunta_id, respuesta_id):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    try:
        respuesta = aceptar_respuesta(
            pregunta_id=pregunta_id,
            respuesta_id=respuesta_id,
            usuario_id=datos.get("autor_id") or datos.get("usuario_id"),
        )
    except ErrorNoEncontrado as error:
        return {"errores": error.errores}, 404
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return _a_diccionario(respuesta), 200