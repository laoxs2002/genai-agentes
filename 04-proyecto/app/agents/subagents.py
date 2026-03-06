"""
Subagentes técnico y comercial. Cada uno tiene sus propias tools y system prompt.
Se exponen como herramientas para el supervisor.
"""
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage

from app.core.config import get_settings

_settings = get_settings()
MODEL = _settings.model_name


# --- Tools del subagente técnico (especificaciones, errores) ---
@tool
def consultar_especificaciones(producto: str) -> str:
    """Consulta especificaciones técnicas de productos. Usa: router, camara, altavoz."""
    datos = {
        "router": "Router Nubis R7: LED rojo indica sin conexión WAN. Reinicio: mantener botón 10 s. Alcance: 120 m². Puertos: 4 LAN + 1 WAN.",
        "camara": "Cámara Vigil Pro: Resolución 4K a 30fps. Ángulo 130°. Almacenamiento SD hasta 256 GB. Códigos error: E-204 (SD llena), E-301 (sin red).",
        "altavoz": "Altavoz SoundMax: 20W RMS. Bluetooth 5.3. Autonomía 12 h. Entrada aux 3.5 mm.",
    }
    clave = next((k for k in datos if k in producto.lower()), None)
    return datos.get(clave, f"Producto '{producto}' no encontrado. Disponibles: router, camara, altavoz.")


@tool
def consultar_codigos_error(codigo: str) -> str:
    """Consulta significado de códigos de error de productos. Ejemplos: E-204, E-301."""
    codigos = {
        "e-204": "E-204: Tarjeta SD llena. Borre grabaciones o use una SD de mayor capacidad.",
        "e-301": "E-301: Sin conexión de red. Compruebe el cable Ethernet y el router.",
        "e-102": "E-102: Sensor de movimiento obstruido. Limpie la lente.",
    }
    return codigos.get(codigo.lower().strip(), f"Código {codigo} no registrado. Consulte el manual en la documentación.")


# --- Tools del subagente comercial (precios, garantías) ---
@tool
def consultar_precios(producto: str) -> str:
    """Consulta precios, planes y garantías. Usa: router, camara, altavoz."""
    catalogo = {
        "router": "Router Nubis R7: 89 EUR. Garantía 2 años. Soporte 24/7 incluido.",
        "camara": "Cámara Vigil Pro: 149 EUR. Plan nube: 9 EUR/mes (30 días grabación).",
        "altavoz": "Altavoz SoundMax: 79 EUR. Garantía 1 año. Sin plan adicional.",
    }
    clave = next((k for k in catalogo if k in producto.lower()), None)
    return catalogo.get(clave, f"Producto '{producto}' no encontrado. Disponibles: router, camara, altavoz.")


@tool
def consultar_garantias(producto: str) -> str:
    """Consulta política de garantía por producto. Usa: router, camara, altavoz."""
    # Referencia a documentación ficticia (RAG puede complementar)
    return "Garantía estándar: 2 años para router, 1 año para cámara y altavoz. Consulte la política completa en la documentación con 'garantía' o 'devoluciones'."


# --- Subagentes ---
_agente_tecnico = None
_agente_comercial = None


def get_agente_tecnico():
    global _agente_tecnico
    if _agente_tecnico is None:
        _agente_tecnico = create_agent(
            model=MODEL,
            tools=[consultar_especificaciones, consultar_codigos_error],
            system_prompt=(
                "Eres un técnico de soporte. Responde solo sobre especificaciones y códigos de error. "
                "Usa las herramientas consultar_especificaciones y consultar_codigos_error. Responde de forma directa y concisa."
            ),
        )
    return _agente_tecnico


def get_agente_comercial():
    global _agente_comercial
    if _agente_comercial is None:
        _agente_comercial = create_agent(
            model=MODEL,
            tools=[consultar_precios, consultar_garantias],
            system_prompt=(
                "Eres un asesor comercial. Responde solo sobre precios, garantías y planes. "
                "Usa las herramientas consultar_precios y consultar_garantias. Responde de forma directa y concisa."
            ),
        )
    return _agente_comercial


# --- Tools para el supervisor (invocar subagentes) ---
def make_invocar_tecnico_tool():
    agente = get_agente_tecnico()

    @tool("soporte_tecnico", description="Resuelve dudas técnicas, especificaciones de productos y códigos de error. Delega aquí preguntas sobre cómo funciona un producto, errores E-204, E-301, etc.")
    def invocar_tecnico(consulta: str) -> str:
        resultado = agente.invoke({"messages": [HumanMessage(content=consulta)]})
        msgs = resultado.get("messages", [])
        return msgs[-1].content if msgs else "Sin respuesta."

    return invocar_tecnico


def make_invocar_comercial_tool():
    agente = get_agente_comercial()

    @tool("soporte_comercial", description="Responde preguntas sobre precios, garantías, planes y condiciones comerciales. Delega aquí cuando pregunten cuánto cuesta, garantía, devoluciones.")
    def invocar_comercial(consulta: str) -> str:
        resultado = agente.invoke({"messages": [HumanMessage(content=consulta)]})
        msgs = resultado.get("messages", [])
        return msgs[-1].content if msgs else "Sin respuesta."

    return invocar_comercial
