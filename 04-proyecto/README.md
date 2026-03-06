# API Soporte – Asistente con base de conocimiento

API REST que simula un producto real de soporte al cliente: un único asistente que usa **LangChain** (agentes, tools, RAG, memoria a corto y largo plazo, subagentes) por debajo. La API expone recursos de producto: conversaciones, mensajes, perfil de usuario, tickets y indexación de documentación.

Autor: Alan Sastre

## Requisitos

- **Python 3.13.5** (gestor **uv**)
- **Docker** (PostgreSQL con imagen pgvector)
- Cuentas con API key: **OpenAI** (gpt-5-nano y text-embedding-3-small), **Tavily** (búsqueda web)


Montar entorno:

```bash
uv python install 3.13.5

uv init --python 3.13.5
uv venv --python 3.13.5

# windows:
.venv\Scripts\activate
# linux mac
source .venv/Scripts/activate

uv add -r requirements.txt
```


## Arranque

1. **Levantar PostgreSQL (pgvector)**
   ```bash
   docker-compose up -d
   ```
   - Un único contenedor Postgres con extensión pgvector en `localhost:5434` (checkpointer, store y RAG usan la misma BD).

2. **Configurar variables de entorno**
   - Copiar `.env.example` a `.env`
   - Rellenar al menos: `OPENAI_API_KEY`, `TAVILY_API_KEY`
   - Opcional: `MODEL_NAME`, `EMBEDDING_MODEL`, `DATABASE_URL`, `RAG_COLLECTION_NAME`, `docs_path`

3. **Instalar y ejecutar**
   ```bash
   uv sync
   uv run fastapi dev app/main.py
   ```

4. **Abrir Swagger**
   - http://127.0.0.1:8000/docs

5. **Indexar documentación (RAG)**  
   Antes de hacer preguntas que dependan de la base de conocimiento:
   - En Swagger: `POST /api/v1/admin/index-docs`
   - Indexa el contenido de `docs/` en PostgreSQL (pgvector, embeddings OpenAI). Ejecutar también tras añadir o cambiar archivos en `docs/`.

---

## Guía para clase (orden recomendado)

Sigue este orden para no perderte. Todo se hace desde la misma máquina: terminal para levantar servicios y navegador para probar la API.

1. **Terminal 1:** Entra en la carpeta del proyecto y levanta Postgres:
   ```bash
   cd ow/05-genai-agents/04-proyecto-codigo
   docker-compose up -d
   ```
   Espera unos segundos la primera vez.

2. **Configuración:** Copia `.env.example` a `.env` y rellena `OPENAI_API_KEY` y `TAVILY_API_KEY` (sin ellas el agente no funcionará).

3. **Terminal 2 (o la misma):** Instala e inicia FastAPI:
   ```bash
   uv sync
   uv run fastapi dev app/main.py
   ```
   Deja esta terminal abierta. Verás algo como `Uvicorn running on http://127.0.0.1:8000`.

4. **Navegador:** Abre http://127.0.0.1:8000/docs (Swagger). Aquí harás el resto de pasos.

5. **Indexar (obligatorio antes de preguntas sobre manuales/garantías):** En Swagger, **POST /api/v1/admin/index-docs** → *Execute*. Debe devolver `chunks_indexed` > 0. Si falla, mira la sección [Problemas frecuentes](#problemas-frecuentes).

6. **Crear una conversación:** **POST /api/v1/conversations** → body vacío `{}` o sin body → *Execute*. Copia el `id` de la respuesta (lo necesitas para enviar mensajes).

7. **Enviar mensajes y verificar:** Usa **POST /api/v1/conversations/{id}/messages** sustituyendo `{id}` por el id copiado. Body: `{"content": "tu mensaje"}`. Sigue los pasos 1–7 de la sección [Verificación paso a paso](#verificación-paso-a-paso-swagger) para comprobar RAG, memoria corto/largo plazo, Tavily, subagentes y tickets.

## Documentación ficticia (`docs/`)

En `docs/` hay documentación **ficticia** que el modelo no conoce de entrenamiento, para poder validar el RAG:

- **manual-producto-nubis.md**: manual del router Nubis R7, códigos E-204, E-301, E-102.
- **politica-garantias.md**: política de garantías TecnoShop, plazos, código TEC-GAR-ES.
- **faq-soporte.md**: FAQ con productos, precios y horarios de soporte.

Preguntas como “¿Qué significa el error E-204?” o “¿Cuál es la política de garantía?” solo se responden bien si se ha indexado `docs/` y el agente usa la herramienta de búsqueda en documentación.

## Resumen de endpoints

| Recurso | Método | Descripción |
|--------|--------|-------------|
| Conversaciones | `POST /api/v1/conversations` | Crear conversación. Body opcional: `{"user_id": "id"}` para long-term memory. |
| Mensajes | `POST /api/v1/conversations/{id}/messages` | Enviar mensaje. Body: `{"content": "texto"}`. El `user_id` se obtiene de la conversación. |
| Perfil | `GET/PUT /api/v1/users/{user_id}/profile` | Leer/actualizar perfil (long-term store). |
| Tickets | `GET /api/v1/tickets` | Listar tickets creados por el agente. |
| Admin | `POST /api/v1/admin/index-docs` | Indexar `docs/` en PGVector (RAG). |

---

## Verificación paso a paso (Swagger)

Todos los pasos se hacen en **http://127.0.0.1:8000/docs** con la app y Postgres levantados.

### Paso 1: Indexar documentación (RAG)

Antes de probar preguntas sobre manuales o garantías: **POST /api/v1/admin/index-docs** (sin body). **Comprobar:** Respuesta `200` con `chunks_indexed` > 0.

### Paso 2: Probar RAG (base de conocimiento)

1. **POST /api/v1/conversations** → body `{}` o sin body. Anota el `id`.
2. **POST /api/v1/conversations/{id}/messages** con body: `{"content": "¿Qué significa el error E-204 del router Nubis y qué debo hacer?"}`.
3. **Comprobar:** La respuesta menciona contenido de la documentación (p. ej. tarjeta SD llena). Otra pregunta: `"¿Cuál es la política de garantía y el código para reclamar?"` → TEC-GAR-ES, plazos.

### Paso 3: Probar memoria a corto plazo (short-term)

El asistente recuerda lo dicho **en la misma conversación** (checkpointer por `conversation_id`).

1. `POST /api/v1/conversations` → anota el `id` de la conversación.
2. `POST /api/v1/conversations/{id}/messages` con body `{"content": "Me llamo Ana y mi producto es el Nubis R7."}`.
3. En la **misma** conversación, `POST .../messages` con `{"content": "¿Cómo me llamo y qué producto tengo?"}`.

**Comprobar:** La respuesta usa “Ana” y “Nubis R7” porque está en el historial del hilo (checkpointer).

### Paso 4: Probar memoria a largo plazo (long-term) y perfil

El perfil se persiste **entre conversaciones** mediante el `user_id` con el que se creó la conversación.

1. `POST /api/v1/conversations` con body `{"user_id": "usuario-test-1"}` → anota el `id`.
2. Envía un mensaje pidiendo guardar una preferencia, por ejemplo: `{"content": "Guarda que mi producto favorito es el Vigil Pro."}`.
3. Comprueba el perfil: `GET /api/v1/users/usuario-test-1/profile` → debe aparecer la preferencia (p. ej. `producto_favorito` o similar).
4. Crea una **nueva** conversación con el mismo `user_id`: `POST /api/v1/conversations` con `{"user_id": "usuario-test-1"}`.
5. En esa nueva conversación, envía: `{"content": "¿Cuál es mi producto favorito?"}`.

**Comprobar:** Responde con “Vigil Pro” (o el valor guardado) usando el store, aunque sea otra conversación.

### Paso 5: Probar búsqueda web (Tavily)

1. Usa una conversación existente o crea una con **POST /api/v1/conversations**.
2. **POST /api/v1/conversations/{id}/messages** con algo como: `{"content": "Busca en internet noticias recientes sobre LangChain o inteligencia artificial y dime un titular."}`.
3. **Comprobar:** La respuesta hace referencia a resultados de búsqueda (el agente usa Tavily). Requiere `TAVILY_API_KEY` en `.env`.

### Paso 6: Probar subagentes (técnico y comercial)

El supervisor delega en subagentes según el tipo de consulta.

1. Pregunta **técnica**: `{"content": "El router me da error E-301, ¿qué hago?"}` → debe usar subagente técnico (manual, códigos de error).
2. Pregunta **comercial**: `{"content": "¿Cuánto cuesta el Vigil Pro y qué garantía tiene?"}` → debe usar subagente comercial (precios, garantías).
3. Pregunta **mixta**: `{"content": "Tengo un Nubis R7 con E-204 y quiero saber si está en garantía"}` → puede usar ambos (documentación + política de garantía).

**Comprobar:** Respuestas alineadas con la documentación ficticia (precios, códigos, plazos) y uso de las herramientas correspondientes.

### Paso 7: Probar creación de tickets

1. **POST /api/v1/conversations/{id}/messages** con: `{"content": "No puedo resolver mi problema, quiero abrir un ticket de soporte para el error E-204 en mi Nubis R7."}`.
2. **Comprobar:** La respuesta indica que se ha creado un ticket (y en el JSON puede venir `ticket_created: true`).
3. **GET /api/v1/tickets** → debe listar el ticket recién creado (título, descripción, prioridad).

## Estructura del proyecto

- `app/main.py`: FastAPI, lifespan (PostgresSaver, PostgresStore, PGVector, supervisor).
- `app/core/config.py`: configuración (pydantic-settings).
- `app/core/langchain.py`: referencias a checkpointer, store, vector_store (PGVector), embeddings.
- `app/agents/supervisor.py`: agente supervisor (create_agent con tools y memoria).
- `app/agents/subagents.py`: subagentes técnico y comercial.
- `app/agents/tools.py`: tools RAG, Tavily, crear_ticket, guardar_preferencia.
- `app/agents/rag.py`: indexación de `docs/` en PostgreSQL (langchain-postgres PGVector).
- `app/api/v1/endpoints/`: conversaciones, usuarios, tickets, admin (index-docs).
- `app/services/chat.py`: invocación del supervisor con thread_id y context.

## Persistencia en PostgreSQL

Una sola base de datos (imagen **pgvector**) sirve para todo:

- **Short-term y long-term memory**: `langgraph-checkpoint-postgres` (PostgresSaver para checkpoints de conversación, PostgresStore para perfil/preferencias). Ver [memory (postgres)](https://reference.langchain.com/python/langchain-classic/memory/chat_message_histories/postgres).
- **RAG**: `langchain-postgres` (PGVector). Ver [Build a semantic search engine (PGVector)](https://docs.langchain.com/oss/python/langchain/knowledge-base#pgvector).

### Checkpointer (memoria a corto plazo – conversación)

- **Paquete**: `langgraph-checkpoint-postgres` (`PostgresSaver`).
- **Tablas**: `checkpoints`, `checkpoint_blobs`, `checkpoint_writes`, `checkpoint_migrations`.
- **Qué guarda**: estado del grafo por hilo (`thread_id` = `conversation_id`): mensajes y metadatos (short-term).

### Store (memoria a largo plazo – perfil y preferencias)

- **Paquete**: `langgraph` / store postgres (`PostgresStore`).
- **Qué guarda**: perfil y preferencias (`guardar_preferencia`, `GET/PUT /api/v1/users/{user_id}/profile`).

### PGVector (RAG)

- **Paquete**: `langchain-postgres` (`PGVector`).
- **Qué guarda**: embeddings de los chunks de `docs/` para búsqueda semántica.

## Problemas frecuentes

| Síntoma | Qué comprobar |
|--------|----------------|
| **index-docs devuelve 503** o "Vector store no disponible" | Postgres está levantado (`docker-compose up -d`) y la app se ha iniciado después. Revisa que el puerto sea 5434 y que `DATABASE_URL` en `.env` coincida. |
| **index-docs devuelve 0 chunks** o "carpeta no existe" | Existe la carpeta `docs/` en la raíz del proyecto (junto a `app/`) y contiene archivos `.md`. |
| **Error al enviar mensaje** (500 o timeout) | `OPENAI_API_KEY` en `.env` es correcta. Sin ella el LLM no responde. |
| **La búsqueda web (Tavily) no responde** | `TAVILY_API_KEY` en `.env`. El Paso 5 de verificación requiere Tavily. |
| **"Conversation not found" (404)** | El `id` en la URL debe ser el que devolvió **POST /conversations**. La lista de IDs válidos está en memoria: si reinicias la app, esa lista se vacía y la API ya no reconoce los IDs antiguos (el historial de mensajes sigue en Postgres, pero para seguir chateando debes crear una **nueva** conversación). |
| **El agente no usa la documentación** | Has ejecutado **POST /api/v1/admin/index-docs** antes de preguntar. Las preguntas deben ser sobre temas de los .md (p. ej. error E-204, garantías, FAQ). |

## Notas

- Sin `.env` con `OPENAI_API_KEY` las llamadas al modelo fallarán. Sin Postgres levantado, la app usa memoria en RAM (InMemorySaver/InMemoryStore) y no tendrá RAG hasta que Postgres (pgvector) esté disponible y se llame a index-docs.
- La primera vez que levantes Postgres, espera unos segundos tras `docker-compose up -d` antes de arrancar la app.
- Para enviar mensajes solo hace falta el body `{"content": "..."}`; el `user_id` (para perfil y preferencias) se obtiene de la conversación, que puede crearse con `{"user_id": "..."}` opcional.
- **Short-term memory (mensajes de la conversación):** Los mensajes se guardan en PostgreSQL (checkpointer). No se pierden al reiniciar. Lo que sí está en memoria es la **lista de IDs de conversación** que la API acepta: al reiniciar esa lista se vacía, así que la API devolverá 404 para IDs antiguos y hay que crear una nueva conversación (el historial anterior sigue en la BD pero la API ya no lo asocia a ningún id válido).
- **Tickets:** La lista de tickets creados por el agente está solo en memoria; al reiniciar la app se pierde.
- **Perfil (long-term):** En Postgres; persiste entre reinicios.
