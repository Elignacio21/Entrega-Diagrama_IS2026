from flask import Blueprint, request

from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.services.catalogo_service import listar_categorias
from qa_platform.services.pregunta_service import crear_pregunta, listar_preguntas
from qa_platform.services.voto_service import votar_pregunta

preguntas_bp = Blueprint("preguntas", __name__, url_prefix="/api/preguntas")


def _a_diccionario(pregunta) -> dict:
    return {
        "identificacion": pregunta.identificacion,
        "titulo": pregunta.titulo,
        "cuerpo": pregunta.cuerpo,
        "fecha": pregunta.fecha.isoformat(),
        "autor_id": pregunta.autor.identificacion,
        "categoria": pregunta.categoria.nombre,
        "etiquetas": [e.nombre for e in pregunta.etiquetas],
        "puntuacion": pregunta.calcularPuntuacion(),
    }


@preguntas_bp.post("")
def registrar_pregunta():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    # La fecha y el identificador no se leen del cliente: los fija el sistema.
    try:
        pregunta = crear_pregunta(
            autor_id=datos.get("autor_id"),
            titulo=datos.get("titulo"),
            cuerpo=datos.get("cuerpo"),
            categoria=datos.get("categoria"),
            etiquetas=datos.get("etiquetas", []),
        )
    except ErrorNoEncontrado as error:
        return {"errores": error.errores}, 404
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return _a_diccionario(pregunta), 201


@preguntas_bp.get("")
def obtener_preguntas():
    preguntas = listar_preguntas()
    return {
        "total": len(preguntas),
        "preguntas": [_a_diccionario(p) for p in preguntas],
    }, 200


@preguntas_bp.get("/categorias")
def obtener_categorias():
    return {"categorias": [categoria.nombre for categoria in listar_categorias()]}, 200


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