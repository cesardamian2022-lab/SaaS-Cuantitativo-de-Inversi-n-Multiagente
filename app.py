import os
import streamlit as st
from quant_engine import ejecutar_motor_cuantitativo
from news_analyzer import analizar_impacto_macro_sectorial

# Configuración inicial de la página
st.set_page_config(page_title="Institutional SAA & Portfolio Platform", layout="wide")

st.title("💼 Institutional Strategic Asset Allocation (SAA) & Multi-Sector Platform")
st.markdown("Comité de Inversiones Autónomo | Optimización Cuantitativa, Análisis Sectorial GICS y Simulación Estocástica.")

# --- BARRA LATERAL CON PARÁMETROS ---
with st.sidebar:
    st.header("⚙️ Parámetros del Comité")
    capital = st.number_input("Capital Inicial (USD)", min_value=10000.0, value=1000000.0, step=50000.0)
    horizonte = st.selectbox("Horizonte Temporal (Años)", [1, 3, 5, 10])
    perfil = st.selectbox("Perfil de Riesgo Base", ["Conservador", "Moderado", "Agresivo", "Dinámico"])
    
    st.markdown("---")
    st.subheader("📊 Ponderación por Sectores GICS (%)")
    st.markdown("Define el peso específico para cada sector:")
    
    sec_tech = st.slider("Tecnología (XLK / Semiconductores)", 0, 100, 25)
    sec_staples = st.slider("Consumo Defensivo (XLP)", 0, 100, 10)
    sec_fin = st.slider("Servicios Financieros (XLF)", 0, 100, 15)
    sec_health = st.slider("Healthcare / Salud (XLV)", 0, 100, 10)
    sec_ind = st.slider("Industrial (XLI)", 0, 100, 5)
    sec_cons = st.slider("Consumo Cíclico (XLY)", 0, 100, 5)
    sec_energy = st.slider("Energía (XLE)", 0, 100, 5)
    sec_util = st.slider("Utilities / Servicios Públicos (XLU)", 0, 100, 5)
    sec_re = st.slider("Bienes Raíces / Real Estate (VNQ)", 0, 100, 5)
    sec_comm = st.slider("Servicios de Comunicación (XLC)", 0, 100, 5)
    sec_mat = st.slider("Materiales Básicos (XLB)", 0, 100, 5)
    rf_global = st.slider("Renta Fija Global / Bonos (AGG)", 0, 100, 10)
    cash_eq = st.slider("Cash / Equivalentes / Depósitos", 0, 100, 5)

    suma_pesos = (sec_tech + sec_staples + sec_fin + sec_health + sec_ind + 
                  sec_cons + sec_energy + sec_util + sec_re + sec_comm + 
                  sec_mat + rf_global + cash_eq)
    
    st.metric("Suma Total de Ponderaciones", f"{suma_pesos}%", delta="Debe sumar 100%" if suma_pesos != 100 else "Óptimo")
    
    restriccion_libre = st.text_area("Condiciones especiales / Tesis (Ej: Enfoque ESG, bonos sostenibles)")
    ejecutar = st.button("🚀 Ejecutar Comité de Inversión SAA", type="primary")

# --- FLUJO DE EJECUCIÓN PRINCIPAL ---
if ejecutar:
    if suma_pesos != 100:
        st.warning(f"⚠️ La suma actual de los pesos es {suma_pesos}%. Se procederá a normalizar de forma proporcional.")
    
    with st.spinner("Analizando flujos de noticias globales y cruzando impacto con sectores GICS..."):
        api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
        
        # Análisis táctico vía LLM
        informe_tactico = analizar_impacto_macro_sectorial(api_key)
        
        # Pesos ingresados
        pesos_usuario = {
            "Tecnología (Information Technology)": sec_tech,
            "Consumo Defensivo (Consumer Staples)": sec_staples,
            "Servicios Financieros (Financials)": sec_fin,
            "Healthcare (Salud)": sec_health,
            "Industrial (Industrials)": sec_ind,
            "Consumo Cíclico (Consumer Discretionary)": sec_cons,
            "Energía (Energy)": sec_energy,
            "Utilities (Servicios Públicos)": sec_util,
            "Bienes Raíces (Real Estate)": sec_re,
            "Servicios de Comunicación": sec_comm,
            "Materiales Básicos": sec_mat,
            "Renta Fija Global (Agg)": rf_global,
            "Cash / Equivalentes": cash_eq
        }
        
        if suma_pesos > 0 and suma_pesos != 100:
            factor = 100.0 / suma_pesos
            pesos_usuario = {k: round(v * factor, 2) for k, v in pesos_usuario.items()}
            
        metricas, excel_file = ejecutar_motor_cuantitativo(pesos_usuario, capital, horizonte)
        
        st.success("✅ Análisis cuantitativo institucional generado con éxito.")
        
        # 1. Inteligencia Táctica
        st.markdown("### 🌐 Inteligencia Táctica de Mercado & Impacto Sectorial GICS")
        st.markdown(informe_tactico)
        
        # 2. Tarjetas Ejecutivas
        st.markdown("### 📈 Métricas Clave de Rendimiento")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Patrimonio Gestionado", f"${capital:,.2f}")
        c2.metric("Retorno Anualizado Est.", metricas["Retorno Anualizado Esperado"])
        c3.metric("Volatilidad Anualizada", metricas["Volatilidad Anualizada"])
        c4.metric("Ratio Sharpe (Rf=4%)", metricas["Sharpe Ratio (Rf=4%)"])
        
        # 3. Escenarios Estocásticos
        st.markdown("### 📊 Proyección Estocástica de Cartera a 12 Meses (Monte Carlo)")
        sc1, sc2, sc3 = st.columns(3)
        sc1.error(f"**Escenario de Estrés (P10)**\n\n${metricas['Escenario Peor (P10 - Estrés)']:,.2f}")
        sc2.warning(f"**Escenario Mediano / Normal (P50)**\n\n${metricas['Escenario Normal (P50 - Mediana)']:,.2f}")
        sc3.success(f"**Escenario Expansivo (P90)**\n\n${metricas['Escenario Mejor (P90 - Expansión)']:,.2f}")
        
        # 4. Botón de Descarga Excel
        st.markdown("---")
        st.download_button(
            label="📥 Descargar Reporte Patrimonial en Excel (Multi-pestaña Profesional)",
            data=excel_file,
            file_name="Reporte_SAA_Institucional_GICS.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("👈 Configura la ponderación sectorial y el capital en la barra lateral y presiona **'Ejecutar Comité de Inversión SAA'** para iniciar el análisis.")
