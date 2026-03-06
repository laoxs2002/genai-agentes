# Curso de agentes de IA generativa

[![Python](https://img.shields.io/badge/Python-3.13.5-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.2.10-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0.9-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.133.1-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5--nano-412991?logo=openai&logoColor=white)](https://openai.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-DE5FE9)](https://docs.astral.sh/uv/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Curso de desarrollo de Agentes de IA Generativa para developers.

Creación de agentes con tools, short-term memory, long-term memory, RAG, Middlewares.

Autor: Alan Sastre
---

## Contenido

- [Curso de agentes de IA generativa](#curso-de-agentes-de-ia-generativa)
  - [Autor: Alan Sastre](#autor-alan-sastre)
  - [Contenido](#contenido)
  - [Descripcion general](#descripcion-general)
  - [Requisitos previos](#requisitos-previos)
  - [Instalacion](#instalacion)
    - [1. Instalar uv](#1-instalar-uv)
    - [2. Clonar el repositorio e instalar Python](#2-clonar-el-repositorio-e-instalar-python)
    - [3. Crear entorno virtual e instalar dependencias](#3-crear-entorno-virtual-e-instalar-dependencias)
    - [4. Configurar variables de entorno](#4-configurar-variables-de-entorno)
  - [Estructura del repositorio](#estructura-del-repositorio)
  - [Modulos del curso](#modulos-del-curso)
    - [01 - Landscape](#01---landscape)
    - [02 - Crear un agente](#02---crear-un-agente)
    - [03 - Contexto y memoria](#03---contexto-y-memoria)
    - [04 - Proyecto completo](#04---proyecto-completo)
  - [Tecnologias utilizadas](#tecnologias-utilizadas)
  - [Contribuir](#contribuir)
  - [Licencia](#licencia)

---

## Descripcion general

Este curso proporciona una guía completa para construir agentes de IA generativa, abordando tanto la teoría como la práctica. El contenido está estructurado de forma progresiva:

1. **Fundamentos teóricos**: qué es un agente, el paradigma ReAct, diferencias entre LLM y agente, y el concepto de Agent Engineering.
2. **Creación de agentes**: configuración del entorno, uso de `create_agent`, herramientas (tools) y salidas estructuradas.
3. **Contexto y memoria**: memoria a corto y largo plazo, middleware, RAG con bases de datos vectoriales, MCP y subagentes.
4. **Proyecto de producción**: API REST completa con FastAPI que implementa un asistente de soporte con supervisor, subagentes especializados, RAG y persistencia en PostgreSQL.

El curso utiliza **LangChain 1.x** como framework principal debido a su madurez, flexibilidad y la API simplificada `create_agent` introducida en la versión 1.0.

---

## Requisitos previos

- **Python 3.13.5** o superior
- **uv** como gestor de paquetes y entornos virtuales
- **Docker** y **Docker Compose** para bases de datos
- **Ollama** (opcional) para modelos locales
- Cuenta de **OpenAI** con API key
- Cuenta de **Tavily** con API key (plan gratuito disponible)

---

## Instalacion

### 1. Instalar uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clonar el repositorio e instalar Python

```bash
git clone https://github.com/tu-usuario/genai-agents.git
cd genai-agents

uv python install 3.13.5
```

### 3. Crear entorno virtual e instalar dependencias

```bash
uv venv --python 3.13.5
```

**Windows:**
```powershell
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

```bash
uv add -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus claves de API:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

---

## Estructura del repositorio

```
genai-agents/
├── 01-landscape/           # Fundamentos teóricos
│   ├── 01-fundamentos.ipynb
│   └── 02-agent-sdks.ipynb
├── 02-create-agent/        # Creación de agentes
│   ├── 01-setup.ipynb
│   ├── 02-create-agent.ipynb
│   ├── 03-tools.ipynb
│   └── 04-agent-structured-outputs.ipynb
├── 03-context/             # Memoria y contexto
│   ├── 01-short_term_memory.ipynb
│   ├── 02-long_term_memory.ipynb
│   ├── 03-middleware-builtin.ipynb
│   ├── 04-middleware-custom.ipynb
│   ├── 05-rag.ipynb
│   ├── 06-mcp.ipynb
│   ├── 07-subagents.ipynb
│   └── docker-compose-*.yml
├── 04-proyecto/            # Proyecto completo
│   ├── app/
│   │   ├── agents/         # Supervisor, subagentes, tools, RAG
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración
│   │   ├── schemas/        # Modelos Pydantic
│   │   └── services/       # Lógica de negocio
│   ├── docs/               # Documentación ficticia para RAG
│   ├── docker-compose.yml
│   └── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Modulos del curso

### 01 - Landscape

Introducción teórica al mundo de los agentes de IA.

| Notebook | Contenido |
|----------|-----------|
| `01-fundamentos.ipynb` | Definición de agente, ciclo percepción-razonamiento-acción, origen histórico (Chain of Thought, ReAct, Toolformer), diferencias entre LLM y agente, componentes de un agente, Agent Engineering |
| `02-agent-sdks.ipynb` | Comparativa de SDKs: LangChain/LangGraph, OpenAI Agents SDK, Google ADK, Anthropic Claude Agent SDK, CrewAI |

**Conceptos clave:**
- El bucle de agente (agent loop)
- Paradigma ReAct (Reasoning + Acting)
- Herramientas, memoria y planificación
- Model Context Protocol (MCP)
- Observabilidad y trazabilidad

### 02 - Crear un agente

Configuración del entorno y primeros pasos con agentes.

| Notebook | Contenido |
|----------|-----------|
| `01-setup.ipynb` | Instalación de uv, Python, LangChain, Ollama y Tavily |
| `02-create-agent.ipynb` | Uso de `create_agent`, parámetros, system prompt, gestión de mensajes |
| `03-tools.ipynb` | Definición de herramientas con decoradores, integración de Tavily Search |
| `04-agent-structured-outputs.ipynb` | Generación de respuestas con esquemas predefinidos |

**Ejemplo básico:**
```python
from langchain.agents import create_agent

agent = create_agent("gpt-5-nano")

response = agent.invoke({
    "messages": [{"role": "user", "content": "¿Cuánto es 1 + 1?"}]
})
```

### 03 - Contexto y memoria

Gestión del estado y conocimiento del agente.

| Notebook | Contenido |
|----------|-----------|
| `01-short_term_memory.ipynb` | Memoria de conversación con InMemorySaver, SqliteSaver y PostgresSaver |
| `02-long_term_memory.ipynb` | Perfil y preferencias persistentes con PostgresStore |
| `03-middleware-builtin.ipynb` | Middleware integrado de LangChain |
| `04-middleware-custom.ipynb` | Middleware personalizado para logging, validación y aprobación humana |
| `05-rag.ipynb` | Retrieval-Augmented Generation con PGVector y embeddings de OpenAI |
| `06-mcp.ipynb` | Model Context Protocol para interoperabilidad de herramientas |
| `07-subagents.ipynb` | Arquitecturas multiagente con supervisor y delegación |

**Tipos de memoria:**
- **Corto plazo (checkpointer)**: historial de la conversación actual, persiste por `thread_id`
- **Largo plazo (store)**: perfil y preferencias del usuario, persiste por `user_id`

### 04 - Proyecto completo

API REST de soporte al cliente que integra todos los conceptos del curso.

**Arquitectura:**

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI                              │
├─────────────────────────────────────────────────────────────┤
│  POST /conversations        Crear conversación              │
│  POST /conversations/{id}/messages   Enviar mensaje         │
│  GET/PUT /users/{id}/profile         Perfil usuario         │
│  GET /tickets                        Listar tickets         │
│  POST /admin/index-docs              Indexar RAG            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Supervisor                             │
│  (Agente principal que delega a subagentes)                 │
├──────────────────────┬──────────────────────────────────────┤
│   Subagente técnico  │        Subagente comercial           │
│   - RAG documentación│        - RAG políticas               │
│   - Búsqueda web     │        - Precios y garantías         │
└──────────────────────┴──────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL (pgvector)                   │
├─────────────────────────────────────────────────────────────┤
│  Checkpointer: memoria a corto plazo (conversaciones)       │
│  Store: memoria a largo plazo (perfiles)                    │
│  PGVector: embeddings para RAG                              │
└─────────────────────────────────────────────────────────────┘
```

**Herramientas del agente:**
- `buscar_en_documentacion`: búsqueda semántica en la base de conocimiento (RAG)
- `buscar_en_web`: búsqueda en internet con Tavily
- `crear_ticket`: creación de tickets de soporte
- `guardar_preferencia`: persistir preferencias del usuario

**Ejecución:**

```bash
cd 04-proyecto

# Levantar PostgreSQL con pgvector
docker-compose up -d

# Configurar variables de entorno
cp .env.example .env
# Editar .env con OPENAI_API_KEY y TAVILY_API_KEY

# Instalar dependencias e iniciar
uv sync
uv run fastapi dev app/main.py

# Abrir Swagger UI
# http://127.0.0.1:8000/docs
```

Consulta el [README del proyecto](04-proyecto/README.md) para una guía detallada de verificación paso a paso.

---

## Tecnologias utilizadas

| Categoría | Tecnología | Versión | Descripción |
|-----------|------------|---------|-------------|
| **Lenguaje** | Python | 3.13.5 | Lenguaje principal |
| **Gestor de paquetes** | uv | - | Gestor moderno de entornos y dependencias |
| **Framework de agentes** | LangChain | 1.2.10 | Framework principal para agentes |
| **Grafos de estado** | LangGraph | 1.0.9 | Control de flujo y checkpointing |
| **API REST** | FastAPI | 0.133.1 | Framework web asíncrono |
| **LLM** | OpenAI GPT-5-nano | - | Modelo de lenguaje principal |
| **Embeddings** | text-embedding-3-small | - | Embeddings para RAG |
| **Búsqueda web** | Tavily | - | API de búsqueda optimizada para agentes |
| **Base de datos** | PostgreSQL + pgvector | - | Persistencia y búsqueda vectorial |
| **Contenedores** | Docker Compose | - | Orquestación de servicios |
| **Modelos locales** | Ollama | - | Ejecución local de modelos (opcional) |
| **Observabilidad** | LangSmith | - | Trazabilidad y evaluación (opcional) |

---

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m "Añade nueva funcionalidad"`)
4. Sube la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## Licencia

MIT.
