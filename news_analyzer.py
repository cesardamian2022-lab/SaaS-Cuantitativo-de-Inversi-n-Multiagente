import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

@st.cache_data(ttl=3600)
def extraer_titulares_brutos() -> list:
    """Extrae titulares en crudo de fuentes financieras con caché de 1 hora."""
    noticias = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # 1. Finviz
    try:
        resp = requests.get("https://finviz.com/news.ashx", headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for l in soup.find_all('a', class_='nn-tab-link', limit=6):
                noticias.append(l.text.strip())
    except Exception:
        pass

    # 2. TradingEconomics Markets
    try:
        resp = requests.get("https://tradingeconomics.com/markets", headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for h in soup.find_all('h3', limit=4):
                noticias.append(h.text.strip())
    except Exception:
        pass

    if not noticias:
        noticias = ["Bancos centrales evalúan tasas de interés ante presiones inflacionarias globales."]
        
    return noticias

def analizar_impacto_macro_sectorial(groq_api_key: str) -> str:
    """
    Utiliza el LLM para procesar los titulares y generar una matriz de impacto
    por sector GICS y recomendaciones directas de rebalanceo de portafolio.
    """
    titulares = extraer_titulares_brutos()
    texto_titulares = "\n".join([f"- {t}" for t in titulares])
    
    prompt_sistema = """
    Eres el Comité de Inversiones Cuantitativo de un fondo de alto rendimiento.
    Tu objetivo es analizar los titulares macroeconómicos actuales, identificar el sentimiento de mercado 
    (Risk-On / Risk-Off) y determinar qué sectores GICS se ven beneficiados o perjudicados, 
    proponiendo acciones tácticas concretas para el portafolio.
    """
    
    prompt_usuario = f"""
    Titulares actuales del mercado extraídos en tiempo real:
    {texto_titulares}
    
    Genera un informe táctico estructurado que contenga:
    1. **Entorno Macro y Sentimiento Actual** (Breve síntesis).
    2. **Matriz de Impacto Sectorial GICS** (Sectores a Sobreponderar 🟢, Mantener 🟡, o Infraponderar 🔴).
    3. **Tesis de Movimiento Táctico** (Qué sectores comprar/vender y justificación basada en los datos).
    """
    
    try:
        model = ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        response = model.invoke([
            SystemMessage(content=prompt_sistema),
            HumanMessage(content=prompt_usuario)
        ])
        return response.content
    except Exception as e:
        return f"No se pudo completar el análisis sintáctico de noticias: {str(e)}"
