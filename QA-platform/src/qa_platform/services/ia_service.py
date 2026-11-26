from __future__ import annotations

from datetime import datetime, timedelta

from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.ia import IA
from qa_platform.models.llm import LLM
from qa_platform.models.pregunta import Pregunta
from qa_platform.models.respuesta import Respuesta
from qa_platform.services.pregunta_service import buscar_pregunta, listar_preguntas

ETIQUETA_IA = "#ia-help"
TIEMPO_ESPERA_POR_DEFECTO = timedelta(hours=24)

# Configuración de ejecución: NO se guarda en la base. La IA como autor sí es
# una fila (las respuestas la referencian), pero el proveedor LLM elegido y el
# tiempo de espera siguen siendo estado de la aplicación.
_llm_activo: LLM | None = None
_tiempo_espera: timedelta = TIEMPO_ESPERA_POR_DEFECTO


def obtener_ia() -> IA:
    """Devuelve la fila de IA de la base (la crea la primera vez).

    Una Respuesta necesita un autor guardado, por eso la IA tiene que existir
    como fila en la tabla `autor`/`ia`. El proveedor LLM no es una columna:
    se le asigna acá en cada llamada.
    """
    ia = db.session.scalars(db.select(IA).order_by(IA.identificacion)).first()
    if ia is None:
        ia = IA()
        db.session.add(ia)
        db.session.commit()
    ia.modelo = _llm_activo
    return ia


def obtener_tiempo_espera() -> timedelta:
    """Devuelve el tiempo de espera configurado para preguntas sin respuestas."""
    return _tiempo_espera


def configurar_ia(
    llm: LLM | None = None,
    tiempo_espera: timedelta | None = None,
) -> IA:
    """Configura el proveedor LLM de la IA y/o el tiempo de espera."""
    global _llm_activo, _tiempo_espera

    if llm is not None:
        if not isinstance(llm, LLM):
            raise ErrorValidacion(
                {"modelo": "El proveedor debe implementar la interfaz LLM"}
            )
        _llm_activo = llm

    if tiempo_espera is not None:
        if not isinstance(tiempo_espera, timedelta) or tiempo_espera < timedelta(0):
            raise ErrorValidacion(
                {"tiempo_espera": "El tiempo de espera debe ser un timedelta no negativo"}
            )
        _tiempo_espera = tiempo_espera

    return obtener_ia()


def reiniciar_configuracion_ia() -> None:
    """Restaura la configuración por defecto (útil para aislar tests)."""
    global _llm_activo, _tiempo_espera
    _llm_activo = None
    _tiempo_espera = TIEMPO_ESPERA_POR_DEFECTO


def _normalizar_etiqueta(nombre: str) -> str:
    return nombre.strip().lstrip("#").casefold()


def tiene_etiqueta_ia(pregunta: Pregunta, etiqueta: str = ETIQUETA_IA) -> bool:
    """Detecta si la pregunta incluye la etiqueta que activa la IA (#ia-help)."""
    objetivo = _normalizar_etiqueta(etiqueta)
    return any(_normalizar_etiqueta(e.nombre) == objetivo for e in pregunta.etiquetas)


def ya_respondida_por_ia(pregunta: Pregunta) -> bool:
    """Evita que la IA responda más de una vez la misma pregunta."""
    return any(isinstance(r.autor, IA) for r in pregunta.respuestas)


def supero_tiempo_espera(
    pregunta: Pregunta,
    ahora: datetime | None = None,
    tiempo_espera: timedelta | None = None,
) -> bool:
    """Verifica si transcurrió el tiempo de espera configurado desde la publicación."""
    referencia = ahora if ahora is not None else datetime.now()
    limite = tiempo_espera if tiempo_espera is not None else _tiempo_espera
    return (referencia - pregunta.fecha) >= limite


def responder_pregunta_con_ia(
    pregunta: Pregunta,
    ia: IA | None = None,
) -> Respuesta | None:
    """Genera y guarda una Respuesta usando IA.crearRespuesta() si aún no respondió."""
    if ya_respondida_por_ia(pregunta):
        return None

    agente = ia if ia is not None else obtener_ia()
    respuesta = agente.crearRespuesta(pregunta)
    db.session.add(respuesta)
    db.session.commit()
    return respuesta


def evaluar_pregunta_para_ia(
    pregunta_id: int,
    ahora: datetime | None = None,
    tiempo_espera: timedelta | None = None,
    ia: IA | None = None,
) -> Respuesta | None:
    """Evalúa una pregunta y responde con IA si tiene #ia-help o venció el tiempo sin respuestas."""
    pregunta = buscar_pregunta(pregunta_id)
    if pregunta is None:
        raise ErrorNoEncontrado({"pregunta": "La pregunta no existe"})

    if ya_respondida_por_ia(pregunta):
        return None

    sin_respuestas = len(pregunta.respuestas) == 0
    activa_por_etiqueta = tiene_etiqueta_ia(pregunta)
    activa_por_tiempo = sin_respuestas and supero_tiempo_espera(
        pregunta, ahora=ahora, tiempo_espera=tiempo_espera
    )

    if activa_por_etiqueta or activa_por_tiempo:
        return responder_pregunta_con_ia(pregunta, ia=ia)

    return None


def procesar_respuestas_automaticas(
    ahora: datetime | None = None,
    tiempo_espera: timedelta | None = None,
    ia: IA | None = None,
) -> list[Respuesta]:
    """Recorre todas las preguntas y genera respuestas automáticas cuando corresponde."""
    generadas: list[Respuesta] = []
    for pregunta in listar_preguntas():
        if pregunta.identificacion is not None:
            respuesta = evaluar_pregunta_para_ia(
                pregunta.identificacion,
                ahora=ahora,
                tiempo_espera=tiempo_espera,
                ia=ia,
            )
            if respuesta is not None:
                generadas.append(respuesta)
    return generadas