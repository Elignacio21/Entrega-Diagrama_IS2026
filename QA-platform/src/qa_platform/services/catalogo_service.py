from qa_platform.models.categoria import Categoria

# Catálogo fijo de categorías disponibles. Las preguntas solo pueden usar
# categorías de esta lista ("categoría existente"). Cuando haya persistencia
# pasará a ser una tabla.
_CATEGORIAS = (
    Categoria("Programacion"),
    Categoria("Algoritmos y estructuras de datos"),
    Categoria("Bases de datos"),
    Categoria("Redes"),
    Categoria("Sistemas operativos"),
    Categoria("Ingenieria de software"),
    Categoria("Matematica"),
    Categoria("Otros"),
)


def listar_categorias() -> list[Categoria]:
    """Devuelve todas las categorías disponibles."""
    return list(_CATEGORIAS)


def buscar_categoria(nombre) -> Categoria | None:
    """Busca una categoría por nombre, sin distinguir mayúsculas.

    Devuelve la categoría del catálogo, o None si no existe.
    """
    if not isinstance(nombre, str):
        return None

    buscado = nombre.strip().casefold()
    for categoria in _CATEGORIAS:
        if categoria.nombre.casefold() == buscado:
            return categoria
    return None
