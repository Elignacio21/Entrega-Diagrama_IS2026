from flask import request

from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.services.voto_service import votar_pregunta


@preguntas_bp.post("/<int:pregunta_id>/votar")
def registrar_voto_pregunta(pregunta_id):
    """Adaptador HTTP para votar una pregunta."""

def _a_diccionario(pregunta) -> dict:
    return {
        "identificacion": pregunta.identificacion,
        "titulo": pregunta.titulo,
        "cuerpo": pregunta.cuerpo,
        "fecha": pregunta.fecha.isoformat(),
        "categoria": pregunta.categoria.nombre,
        "etiquetas": [etiqueta.nombre for etiqueta in pregunta.etiquetas],
        "autor_id": pregunta.autor.identificacion,
        "puntuacion": pregunta.calcularPuntuacion(),
    }


@preguntas_bp.post("/preguntas")
def registrar_pregunta():
    """Adaptador HTTP: traduce JSON <-> dominio. Las reglas viven en el modelo."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

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


@preguntas_bp.get("/preguntas")
def obtener_preguntas():
    preguntas = listar_preguntas()
    return {
        "total": len(preguntas),
        "preguntas": [_a_diccionario(pregunta) for pregunta in preguntas],
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
