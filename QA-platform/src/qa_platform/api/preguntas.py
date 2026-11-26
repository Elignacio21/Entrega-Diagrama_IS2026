from flask import request

from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.services.voto_service import votar_pregunta


@preguntas_bp.post("/<int:pregunta_id>/votar")
def registrar_voto_pregunta(pregunta_id):
    """Adaptador HTTP para votar una pregunta."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    try:
        pregunta = votar_pregunta(
            pregunta_id=pregunta_id,
            usuario_id=datos.get("autor_id") or datos.get("usuario_id"),
            tipo=datos.get("tipo"),
        )
    except ErrorNoEncontrado as error:
        return {"errores": error.errores}, 404
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return {
        "pregunta_id": pregunta.identificacion,
        "puntuacion": pregunta.calcularPuntuacion(),
    }, 200