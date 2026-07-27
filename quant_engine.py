import io
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

@st.cache_data(ttl=86400)
def ejecutar_motor_cuantitativo(pesos_dict: dict, capital_inicial: float, horizonte_anos: int = 1):
    """
    Descarga precios históricos ajustados, calcula métricas de riesgo/retorno,
    simula escenarios estocásticos y genera un libro Excel profesional multi-pestaña.
    """
    proxy_tickers = {
        "Renta Variable Global": "SPY",
        "Renta Fija Global": "AGG",
        "Real Estate / Infra": "VNQ",
        "Cash / Ahorro": "SHV",
        "Alternativos / Commodities": "GLD"
    }
    
    tickers = [proxy_tickers.get(k, "SPY") for k in pesos_dict.keys()]
    pesos = np.array(list(pesos_dict.values())) / 100.0
    
    # Descarga de datos históricos (3 años)
    data = yf.download(tickers, period="3y", progress=False)["Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()
        
    returns = data.pct_change().dropna()
    mu = returns.mean() * 252
    cov = returns.cov() * 252
    
    portfolio_return = np.dot(pesos, mu)
    portfolio_vol = np.sqrt(np.dot(pesos.T, np.dot(cov, pesos)))
    
    # Simulación de escenarios a 12 meses (horizonte de proyección)
    np.random.seed(42)
    simulaciones = 1000
    resultados_finales = []
    
    for _ in range(simulaciones):
        shock = np.random.normal(portfolio_return, portfolio_vol)
        valor_final = capital_inicial * (1 + shock)
        resultados_finales.append(valor_final)
        
    percentiles = np.percentile(resultados_finales, [10, 50, 90])
    
    metricas = {
        "Capital Inicial": capital_inicial,
        "Retorno Anualizado Esperado": f"{round(portfolio_return * 100, 2)}%",
        "Volatilidad Anualizada": f"{round(portfolio_vol * 100, 2)}%",
        "Sharpe Ratio (Rf=4%)": round((portfolio_return - 0.04) / portfolio_vol, 2),
        "Escenario Peor (P10 - Estrés)": round(percentiles[0], 2),
        "Escenario Normal (P50 - Mediana)": round(percentiles[1], 2),
        "Escenario Mejor (P90 - Expansión)": round(percentiles[2], 2)
    }
    
    # Generación de Excel en Memoria (Multi-pestaña tipo tu muestra)
    output = io.BytesIO()
    wb = Workbook()
    
    # Hoja 1: Resumen
    ws_resumen = wb.active
    ws_resumen.title = "Resumen"
    ws_resumen.append(["RESUMEN DE INVERSIONES INSTITUCIONALES"])
    ws_resumen.append(["Activo / Tipo", "Porcentaje (%)", "Valor de Mercado (USD)", "Retorno Esperado"])
    
    for activo, peso in pesos_dict.items():
        valor = capital_inicial * (peso / 100.0)
        ws_resumen.append([activo, f"{peso}%", valor, f"{round(portfolio_return*100, 2)}%"])
        
    # Hoja 2: Rentabilidad
    ws_rent = wb.create_sheet(title="Rentabilidad")
    ws_rent.append(["Métrica de Rentabilidad TWR", "Valor"])
    ws_rent.append(["Retorno Acumulado Anual", metricas["Retorno Anualizado Esperado"]])
    ws_rent.append(["Volatilidad de Cartera", metricas["Volatilidad Anualizada"]])
    ws_rent.append(["Ratio Sharpe", metricas["Sharpe Ratio (Rf=4%)"]])
    
    # Hoja 3: Rendimiento Escenarios
    ws_rend = wb.create_sheet(title="Rendimiento")
    ws_rend.append(["Escenario de Mercado (12 Meses)", "Valor Proyectado (USD)"])
    ws_rend.append(["Escenario Peor (P10)", metricas["Escenario Peor (P10 - Estrés)"]])
    ws_rend.append(["Escenario Normal (P50)", metricas["Escenario Normal (P50 - Mediana)"]])
    ws_rend.append(["Escenario Mejor (P90)", metricas["Escenario Mejor (P90 - Expansión)"]])
    
    wb.save(output)
    output.seek(0)
    
    return metricas, output
