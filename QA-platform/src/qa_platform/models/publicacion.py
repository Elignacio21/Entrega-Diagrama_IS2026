from datetime import UTC, datetime


class Publicacion:
    """Base común de Pregunta y Respuesta (clase abstracta).

    No se puede instanciar directamente: solo existe para compartir el
    contenido (cuerpo), la fecha y el cálculo de la puntuación.

    Se comprueba en el constructor, igual que en Autor. No se usa ABC porque
    ABC solo bloquea la instanciación cuando hay un método abstracto, y
    calcularPuntuacion() será concreto (lo comparten Pregunta y Respuesta).
    """

    def __init__(self, cuerpo: str, fecha: datetime | None = None):
        if type(self) is Publicacion:
            raise TypeError(
                "Publicacion es abstracta y no puede instanciarse directamente"
            )
        self.cuerpo = cuerpo
        self.fecha = fecha if fecha is not None else datetime.now(UTC)

    def calcularPuntuacion(self) -> int:
        """Puntuación de la publicación: votos positivos menos negativos.

        Todavía no existen los votos (issue #9), así que por ahora es 0.
        """
        return 0