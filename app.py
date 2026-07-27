import streamlit as st
from quant_engine import ejecutar_motor_cuantitativo
from news_scraper import obtener_noticias_mercado

st.set_page_config(page_title="Quantitative SAA Platform", layout="wide")

st.title("💼 Quantitative Strategic Asset Allocation (SAA) Platform")
st.markdown("Sistema institucional para optimización de portafolios, simulación de escenarios y control patrimonial.")

# --- BARRA LATERAL CON PARÁMETROS AVANZADOS ---
with st.sidebar:
    st.header("Parámetros del Comité")
    capital = st.number_input("Capital Inicial (USD)", min_value=10000.0, value=1000000.0, step=50000.0)
    horizonte = st.selectbox("Horizonte Temporal (Años)", [1, 3, 5, 10])
    perfil = st.selectbox("Perfil de Riesgo", ["Conservador", "Moderado", "Agresivo", "Dinámico"])
    
    st.markdown("---")
    st.subheader("Restricciones Personalizadas (Opcional)")
    sesgo_tech = st.slider("Sesgo Sector Tecnología", 0.0, 0.5, 0.2)
    sesgo_consumo = st.slider("Sesgo Consumo Básico (Defensivo)", 0.0, 0.5, 0.2)
    restriccion_libre = st.text_area("Condiciones especiales (Ej: Bonos sostenibles ESG, mercados emergentes)")

    ejecutar = st.button("Ejecutar Análisis y Simulación SAA", type="primary")

if ejecutar:
    with st.spinner("Analizando fuentes de mercado (Bloomberg, Finviz, TradingEconomics) y ejecutando motor cuantitativo..."):
        noticias = obtener_noticias_mercado()
        
        # Pesos base según perfil con ajustes de restricciones
        if perfil == "Conservador":
            pesos = {"Renta Fija Global": 65, "Cash / Ahorro": 25, "Renta Variable Global": 10}
        elif perfil == "Moderado":
            pesos = {"Renta Fija Global": 45, "Renta Variable Global": 40, "Real Estate / Infra": 10, "Cash / Ahorro": 5}
        else:
            pesos = {"Renta Variable Global": 60, "Alternativos / Commodities": 20, "Renta Fija Global": 20}
            
        metricas, excel_file = ejecutar_motor_cuantitativo(pesos, capital, horizonte)
        
        st.success("¡Análisis cuantitativo completado con éxito!")
        
        # Visualización en Tarjetas (Métricas Clave)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Capital Inicial", f"${capital:,.2f}")
        col2.metric("Retorno Esperado", metricas["Retorno Anualizado Esperado"])
        col3.metric("Volatilidad Anual", metricas["Volatilidad Anualizada"])
        col4.metric("Ratio Sharpe", metricas["Sharpe Ratio (Rf=4%)"])
        
        st.markdown("### 📈 Proyección de Escenarios a 12 Meses (Monte Carlo)")
        sc1, sc2, sc3 = st.columns(3)
        sc1.error(f"**Escenario Peor (P10)**\n\n${metricas['Escenario Peor (P10 - Estrés)']:,.2f}")
        sc2.warning(f"**Escenario Normal (P50)**\n\n${metricas['Escenario Normal (P50 - Mediana)']:,.2f}")
        sc3.success(f"**Escenario Mejor (P90)**\n\n${metricas['Escenario Mejor (P90 - Expansión)']:,.2f}")
        
        st.markdown("### 📰 Inteligencia de Mercado Reciente (Scraping Activo)")
        for n in noticias:
            st.info(n)
            
        st.markdown("---")
        st.download_button(
            label="📥 Descargar Reporte Completo en Excel (Multi-pestaña)",
            data=excel_file,
            file_name="Reporte_SAA_Institucional.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Configura los parámetros en la barra lateral y haz clic en **'Ejecutar Análisis y Simulación SAA'** para iniciar el motor institucional.")
