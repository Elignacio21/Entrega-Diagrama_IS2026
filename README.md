# QA Platform

Plataforma colaborativa de preguntas y respuestas (Q&A) para estudiantes
universitarios. Trabajo Práctico Integrador — Ingeniería de Software 2026.

**Stack:** Python 3.12 · Flask · Flask-SQLAlchemy / SQLAlchemy · Alembic ·
SQLite (desarrollo) · pytest · Ruff · uv

## Qué hace la aplicación

- Los usuarios se **registran** (correo + contraseña, guardada con hash).
- Un usuario **publica preguntas** con una categoría (obligatoria, de un
  catálogo fijo) y etiquetas (opcionales).
- Otros usuarios **responden** las preguntas.
- El autor de una pregunta puede **aceptar** una de sus respuestas (máximo una
  por pregunta).
- Cualquier usuario puede **votar** preguntas y respuestas (POSITIVO o
  NEGATIVO, un voto por usuario y publicación). La puntuación es
  positivos − negativos.
- Una **IA** puede responder preguntas automáticamente, usando un proveedor de
  modelo de lenguaje intercambiable (patrón Strategy).

Todos los datos se guardan en una base de datos: sobreviven a reiniciar el
servidor.

## Puesta en marcha

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12+. SQLite viene
incluido con Python: no hay que instalar nada más.

```bash
git clone <repositorio>
cd QA-platform
cp .env.example .env          # y ajustar valores si hace falta
uv sync                       # instala las dependencias exactas de uv.lock

uv run alembic upgrade head                        # crea las tablas
uv run flask --app qa_platform sembrar-categorias  # carga las categorías

uv run flask --app qa_platform run --debug         # arranca en localhost:5000
```

Los dos comandos del medio hay que correrlos **una vez** (y de nuevo si se
borra la base). Sin las categorías, crear una pregunta devuelve
`"La categoría indicada no existe"`.

Verificar que funciona:

```bash
curl http://localhost:5000/health
# {"status":"ok"}
```

También hay una página de prueba para registrar usuarios en
<http://localhost:5000/>.

## Configuración

Se lee de variables de entorno (ver `.env.example`).
**Nunca subir `.env` ni secretos reales a Git.**

| Variable          | Descripción                                   | Por defecto            |
|-------------------|-----------------------------------------------|------------------------|
| `SECRET_KEY`      | Clave secreta de Flask                        | `development-only-key` |
| `DATABASE_URL`    | URL de la base de datos                       | `sqlite:///app.db`     |
| `GEMINI_API_KEY`  | Clave del proveedor Gemini (solo si se usa)   | vacío                  |
| `OPENAI_API_KEY`  | Clave del proveedor OpenAI (solo si se usa)   | vacío                  |
| `LOCAL_LLM_URL`   | URL del modelo local (por ejemplo Ollama)     | `http://localhost:11434` |

Con SQLite, Flask-SQLAlchemy resuelve las rutas relativas dentro de la carpeta
`instance/`. En producción se puede usar PostgreSQL cambiando solo
`DATABASE_URL` (y agregando el driver correspondiente, por ejemplo `psycopg`).

## Probar la API a mano

Con el servidor corriendo, en otra terminal:

```bash
# 1. Dos usuarios (la contraseña debe tener 8+ caracteres)
curl -X POST localhost:5000/api/usuarios -H "Content-Type: application/json" \
  -d '{"correo":"ada@example.com","password":"password123"}'
curl -X POST localhost:5000/api/usuarios -H "Content-Type: application/json" \
  -d '{"correo":"bob@example.com","password":"password123"}'

# 2. Ada publica una pregunta (será la pregunta 1)
curl -X POST localhost:5000/api/preguntas -H "Content-Type: application/json" \
  -d '{"autor_id":1,"titulo":"¿Cómo funciona Flask?","cuerpo":"No entiendo el application factory.","categoria":"Programacion","etiquetas":["flask"]}'

# 3. Bob responde. La respuesta devuelve "identificacion": 2 (ver nota abajo)
curl -X POST localhost:5000/api/preguntas/1/respuestas -H "Content-Type: application/json" \
  -d '{"autor_id":2,"cuerpo":"Es una funcion que crea la app."}'

# 4. Ver las respuestas
curl localhost:5000/api/preguntas/1/respuestas

# 5. Ada acepta la respuesta 2
curl -X POST localhost:5000/api/preguntas/1/respuestas/2/aceptar -H "Content-Type: application/json" \
  -d '{"autor_id":1}'

# 6. Bob vota POSITIVO la pregunta 1
curl -X POST localhost:5000/api/preguntas/1/votar -H "Content-Type: application/json" \
  -d '{"autor_id":2,"tipo":"POSITIVO"}'

# 7. Ada vota POSITIVO la respuesta 2
curl -X POST localhost:5000/api/preguntas/1/respuestas/2/votar -H "Content-Type: application/json" \
  -d '{"autor_id":1,"tipo":"POSITIVO"}'

# 8. Ver las respuestas: ahora refleja esAceptada: true y puntuacion: 1
curl localhost:5000/api/preguntas/1/respuestas
```

> **Los ids de preguntas y respuestas comparten secuencia.** Ambas son
> "publicaciones" y se guardan en la misma tabla base, así que con una pregunta
> como id 1, su primera respuesta es el id **2**. Usá siempre el
> `identificacion` que devuelve la API.

Respuesta típica del paso 8 (el orden de las claves puede variar):

```json
{
  "respuestas": [
    {
      "autor_id": 2,
      "cuerpo": "Es una funcion que crea la app.",
      "esAceptada": true,
      "fecha": "2026-11-26T09:35:58.505330",
      "identificacion": 2,
      "pregunta_id": 1,
      "puntuacion": 1
    }
  ],
  "total": 1
}
```

### Comprobar que los datos persisten

Frená el servidor (Ctrl+C), volvé a arrancarlo y corré:

```bash
curl localhost:5000/api/usuarios
curl localhost:5000/api/preguntas
```

Si Ada, Bob y la pregunta siguen ahí, los datos se están guardando en la base.

### Errores esperados

Si repetís el script, los datos ya existen. Ejemplos de respuestas de error:

```bash
# Correo repetido -> 400
{"errores": {"correo": "El correo ya está registrado"}}

# Pregunta inexistente -> 404
{"errores": {"pregunta": "La pregunta no existe"}}

# Votar dos veces la misma publicación -> 400
{"errores": {"voto": "El usuario ya votó esta publicación"}}

# Aceptar una respuesta sin ser el autor de la pregunta -> 400
{"errores": {"autor": "Solo el autor de la pregunta puede aceptar una respuesta"}}
```

## Endpoints

Todos reciben y devuelven JSON. Los errores devuelven `{"errores": {campo: mensaje}}`
con código `400` (datos inválidos) o `404` (recurso inexistente).

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET  | `/health` | Estado del servicio |
| POST | `/api/usuarios` | Registrar usuario. Body: `correo`, `password` → `201` |
| GET  | `/api/usuarios` | Listar usuarios |
| POST | `/api/preguntas` | Publicar pregunta. Body: `autor_id`, `titulo`, `cuerpo`, `categoria`, `etiquetas` (opcional) → `201` |
| GET  | `/api/preguntas` | Listar preguntas |
| GET  | `/api/preguntas/categorias` | Listar las categorías disponibles |
| POST | `/api/preguntas/<id>/votar` | Votar una pregunta. Body: `autor_id`, `tipo` (`POSITIVO`/`NEGATIVO`) |
| POST | `/api/preguntas/<id>/respuestas` | Responder. Body: `autor_id`, `cuerpo` → `201` |
| GET  | `/api/preguntas/<id>/respuestas` | Listar las respuestas de una pregunta |
| POST | `/api/preguntas/<id>/respuestas/<rid>/aceptar` | Aceptar una respuesta. Body: `autor_id` |
| POST | `/api/preguntas/<id>/respuestas/<rid>/votar` | Votar una respuesta. Body: `autor_id`, `tipo` |
| GET  | `/` | Página de prueba para registrar usuarios |

En los endpoints de votar y aceptar, el usuario puede enviarse como `autor_id`
o como `usuario_id`.

## Reglas de negocio

- **Usuarios:** el correo debe tener formato válido y ser único (se guarda en
  minúsculas); la contraseña debe tener al menos 8 caracteres y se guarda
  siempre como hash, nunca en texto plano.
- **Preguntas:** título y cuerpo obligatorios; la categoría debe existir en el
  catálogo (se compara sin distinguir mayúsculas); las etiquetas son una lista
  de textos no vacíos, se guardan en minúsculas y sin repetir. La fecha y el
  identificador los fija el sistema.
- **Respuestas:** cuerpo obligatorio; nacen sin aceptar.
- **Aceptación:** solo el autor de la pregunta puede aceptar, y una pregunta
  tiene como máximo una respuesta aceptada.
- **Votos:** un usuario vota una sola vez cada publicación. Esta regla la
  verifica el código y también una restricción única en la base de datos.

## Respuestas automáticas con IA

La IA es un autor más (como un usuario) que escribe respuestas usando un
proveedor de modelo de lenguaje intercambiable (patrón **Strategy**). Los
proveedores disponibles en `models/llm.py` son `Gemini`, `OpenIA` y
`ModeloLocal`.

> Por ahora los tres son **simulados**: devuelven un texto de ejemplo y dejan
> marcado el punto donde se integraría el SDK real de cada proveedor.

La IA responde una pregunta cuando:

1. la pregunta lleva la etiqueta `#ia-help`, o
2. pasó el tiempo de espera (24 horas por defecto) sin que nadie responda.

Nunca responde dos veces la misma pregunta. La lógica está en
`services/ia_service.py` (`evaluar_pregunta_para_ia`,
`procesar_respuestas_automaticas`); todavía no hay un endpoint HTTP que la
dispare.

## Modelo de datos

```
Autor (abstracto)               Publicacion (base)
├── Usuario                     ├── Pregunta ── Categoria (1), Etiqueta (0..*)
└── IA                          └── Respuesta ── pertenece a una Pregunta

Voto ── lo emite un Usuario sobre una Publicacion
```

Tablas: `autor`, `usuario`, `ia`, `publicacion`, `pregunta`, `respuesta`,
`voto`, `categoria`, `etiqueta`, `pregunta_etiqueta`.

Se usa **herencia de tabla unida** (*joined table inheritance*): la tabla base
guarda lo común y cada subclase tiene su propia tabla con lo específico.

## Migraciones (Alembic)

```bash
uv run alembic revision --autogenerate -m "descripcion del cambio"
# revisar el archivo generado en migrations/versions/
uv run alembic upgrade head      # aplicar
uv run alembic downgrade -1      # volver atrás
```

Las migraciones son parte del código y se versionan en Git. Toda clase nueva
de `models/` debe importarse en `models/__init__.py`, o Alembic no la ve.

### Empezar con la base de cero

Frená el servidor, borrá el archivo de la base (`app.db` en la carpeta
`instance/`, o donde apunte `DATABASE_URL`) y repetí:

```bash
uv run alembic upgrade head
uv run flask --app qa_platform sembrar-categorias
```

## Tests

```bash
uv run pytest                   # toda la suite
uv run pytest -x                # se detiene en el primer fallo
uv run pytest -q                # salida corta
uv run pytest tests/test_usuario.py                              # un archivo
uv run pytest tests/test_usuario.py::test_el_correo_es_unico     # un test
uv run pytest -k "ia"           # los tests cuyo nombre contenga "ia"
```

Los tests no tocan tu base de desarrollo: `tests/conftest.py` crea para cada
test una base SQLite **en memoria**, con las tablas vacías y las categorías ya
cargadas, y la descarta al terminar. El fixture `app` es `autouse`, así que
todos los tests tienen aplicación y base disponibles; `client` entrega un
cliente HTTP de prueba.

Lint:

```bash
uv run ruff check .
```

## Estructura

```
src/qa_platform/
├── __init__.py       # Application factory: create_app() y comando CLI
├── config.py         # Configuración desde variables de entorno
├── extensions.py     # Instancia compartida de SQLAlchemy (db)
├── errors.py         # ErrorValidacion, ErrorNoEncontrado
├── models/           # Modelos del dominio (tablas)
├── services/         # Lógica de negocio y acceso a la base (incl. IA y LLM)
├── api/              # Blueprints JSON (health, usuarios, preguntas, respuestas)
├── web/              # Blueprints HTML / Jinja2
├── templates/
└── static/
migrations/           # Migraciones de Alembic
tests/                # pytest
```

Los servicios son la única capa que usa `db.session` y hace `commit()`. Los
modelos contienen las reglas del dominio y no conocen la sesión; los blueprints
solo traducen JSON a llamadas de servicio.
