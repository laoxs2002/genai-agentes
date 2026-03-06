import os
from dotenv import load_dotenv

load_dotenv()

def verificar_langchain():
    import langchain
    print(f"LangChain: {langchain.__version__}")

def verificar_ollama():
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="gemma3:1b")
    response = llm.invoke("Responde solo 'OK'")
    print(f"Ollama gemma3:1b: {response.content.strip()}")

def verificar_tavily():
    from langchain_tavily import TavilySearch
    api_key = os.environ.get("TAVILY_API_KEY")
    if api_key:
        print("Tavily: API key configurada")
    else:
        print("Tavily: API key no encontrada")

if __name__ == "__main__":
    print("Verificando entorno...\n")
    
    verificar_langchain()
    verificar_ollama()
    verificar_tavily()
    
    print("\nEntorno verificado correctamente")