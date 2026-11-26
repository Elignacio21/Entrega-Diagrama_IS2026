import inspect
import pytest

from qa_platform.errors import ErrorValidacion
from qa_platform.models import llm as llm_module
from qa_platform.models.autor import Autor
from qa_platform.models.categoria import Categoria
from qa_platform.models.enums import RolUsuario
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.ia import IA
from qa_platform.models.llm import Gemini, LLM, ModeloLocal, OpenIA
from qa_platform.models.pregunta import Pregunta
from qa_platform.models.respuesta import Respuesta
from qa_platform.models.usuario import Usuario


def _crear_pregunta_ejemplo() -> Pregunta:
    estudiante = Usuario(
        identificacion=1,
        correo="estudiante@uni.edu",
        password="hash_seguro_password",
        rol=RolUsuario.USUARIO_GENERAL,
    )
    return Pregunta(
        titulo="¿Qué ventaja tiene el patrón Strategy?",
        cuerpo="Quiero desacoplar los proveedores de IA del dominio.",
        categoria=Categoria("Ingenieria de software"),
        autor=estudiante,
        etiquetas=[Etiqueta("patrones"), Etiqueta("python")],
    )


def test_proveedores_implementan_interfaz_llm():
    gemini = Gemini(api_key="clave-prueba")
    openai = OpenIA(api_key="clave-prueba")
    local = ModeloLocal()

    assert isinstance(gemini, LLM)
    assert isinstance(openai, LLM)
    assert isinstance(local, LLM)


def test_generar_cuerpo_devuelve_string_en_cada_estrategia():
    pregunta = _crear_pregunta_ejemplo()
    estrategias: list[LLM] = [
        Gemini(api_key="clave-prueba"),
        OpenIA(api_key="clave-prueba"),
        ModeloLocal(),
    ]

    for estrategia in estrategias:
        cuerpo = estrategia.generarCuerpo(pregunta)
        assert isinstance(cuerpo, str)
        assert len(cuerpo.strip()) > 0


def test_ia_hereda_de_autor_y_crea_respuesta_polimorfica():
    pregunta = _crear_pregunta_ejemplo()
    ia = IA(llm=Gemini(api_key="clave-prueba"))

    assert isinstance(ia, Autor)

    respuesta = ia.crearRespuesta(pregunta)
    assert isinstance(respuesta, Respuesta)
    assert respuesta.autor is ia
    assert respuesta.pregunta is pregunta
    assert respuesta in pregunta.respuestas
    assert "Gemini" in respuesta.cuerpo


def test_ia_permite_intercambiar_estrategia_sin_conocer_clase_concreta():
    pregunta = _crear_pregunta_ejemplo()
    ia = IA(llm=ModeloLocal())

    r_local = ia.crearRespuesta(pregunta)
    assert "ModeloLocal" in r_local.cuerpo

    ia.llm = OpenIA(api_key="clave-prueba")
    r_openai = ia.crearRespuesta(pregunta)
    assert "OpenIA" in r_openai.cuerpo
    assert len(pregunta.respuestas) == 2


def test_agregar_nuevo_proveedor_sin_modificar_clases_existentes():
    class AnthropicClaude(LLM):
        def generarCuerpo(self, p: Pregunta) -> str:
            return f"[Claude] Explicación sobre {p.titulo}"

    pregunta = _crear_pregunta_ejemplo()
    ia = IA(llm=AnthropicClaude())
    respuesta = ia.crearRespuesta(pregunta)

    assert respuesta.cuerpo == "[Claude] Explicación sobre ¿Qué ventaja tiene el patrón Strategy?"


def test_validaciones_de_llm_y_api_keys(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    pregunta = _crear_pregunta_ejemplo()

    with pytest.raises(ErrorValidacion):
        Gemini(api_key="").generarCuerpo(pregunta)

    with pytest.raises(ErrorValidacion):
        OpenIA(api_key="").generarCuerpo(pregunta)

    with pytest.raises(ErrorValidacion):
        IA(llm="no_es_un_llm")  # type: ignore[arg-type]


def test_lectura_desde_variables_de_entorno(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-gemini-123")
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai-456")

    gemini = Gemini()
    openai = OpenIA()

    assert gemini.api_key == "env-gemini-123"
    assert openai.api_key == "env-openai-456"


def test_no_hay_claves_hardcodeadas_en_codigo():
    codigo_fuente = inspect.getsource(llm_module)
    assert "AIza" not in codigo_fuente
    assert "sk-" not in codigo_fuente