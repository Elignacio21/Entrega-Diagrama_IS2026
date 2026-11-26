from qa_platform.extensions import db
from qa_platform.models.categoria import Categoria
from qa_platform.models.etiqueta import Etiqueta

# Categorías iniciales. Las preguntas solo pueden usar categorías que existan
# en la tabla `categoria` ("categoría existente"). Se cargan con:
#     uv run flask --app qa_platform sembrar-categorias
NOMBRES_CATEGORIAS = (
    "Programacion",
    "Algoritmos y estructuras de datos",
    "Bases de datos",
    "Redes",
    "Sistemas operativos",
    "Ingenieria de software",
    "Matematica",
    "Otros",
)


def sembrar_categorias() -> None:
    """Inserta las categorías iniciales que falten (es idempotente)."""
    existentes = {categoria.nombre for categoria in listar_categorias()}
    for nombre in NOMBRES_CATEGORIAS:
        if nombre not in existentes:
            db.session.add(Categoria(nombre))
    db.session.commit()


def listar_categorias() -> list[Categoria]:
    """Devuelve todas las categorías disponibles."""
    return list(db.session.scalars(db.select(Categoria).order_by(Categoria.id)))


def buscar_categoria(nombre) -> Categoria | None:
    """Busca una categoría por nombre, sin distinguir mayúsculas.

    Devuelve la categoría de la base, o None si no existe.
    """
    if not isinstance(nombre, str):
        return None

    buscado = nombre.strip().casefold()
    for categoria in listar_categorias():
        if categoria.nombre.casefold() == buscado:
            return categoria
    return None


def obtener_o_crear_etiqueta(nombre: str) -> Etiqueta:
    """Devuelve la etiqueta con ese nombre; si no existe, la deja pendiente de guardar.

    Las etiquetas se comparten entre preguntas (una fila por nombre), así que
    nunca hay que crear una segunda "python". No hace commit: lo hace quien la
    llama junto con el resto de los cambios.
    """
    etiqueta = db.session.scalar(db.select(Etiqueta).where(Etiqueta.nombre == nombre))
    if etiqueta is None:
        etiqueta = Etiqueta(nombre)
        db.session.add(etiqueta)
    return etiqueta