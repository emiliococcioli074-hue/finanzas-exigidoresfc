import streamlit as st
import pandas as pd
import datetime
import calendar

st.set_page_config(page_title="Finanzas Exigidores FC", page_icon="⚽", layout="wide")

# --- CONFIGURACIÓN DINÁMICA ---
CUOTA_MENSUAL = 41000
DIAS_ENTRENAMIENTO = ["Tuesday", "Thursday"] # Martes y Jueves
DIA_TORNEO = "Friday" # Viernes

# --- ESTILOS ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    .status-ok { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONEXIÓN Y LIMPIEZA ---
sheet_url = "https://docs.google.com/spreadsheets/d/1gETPp5vu-tWJkMPSHRcrsl5XLuK3nKxtW5stVmO5y80/export?format=csv"

def get_week_of_month(date):
    """Calcula el número de semana dentro del mes."""
    first_day = date.replace(day=1)
    dom = date.day
    adjusted_dom = dom + first_day.weekday()
    return int((adjusted_dom - 1) / 7) + 1

try:
    df_raw = pd.read_csv(sheet_url)
    df_raw.columns = df_raw.columns.str.strip()
    
    # Limpieza de montos
    df_raw["Monto"] = df_raw["Monto"].replace('[\$,]', '', regex=True).astype(float).fillna(0)
    
    # Procesamiento de Fechas
    df_raw["Fecha_DT"] = pd.to_datetime(df_raw["Marca temporal"], dayfirst=True)
    df_raw["Mes_Año"] = df_raw["Fecha_DT"].dt.strftime('%m-%Y')
    df_raw["Dia_Nombre"] = df_raw["Fecha_DT"].dt.day_name()
    df_raw["Semana_Mes"] = df_raw["Fecha_DT"].apply(get_week_of_month)
    
    # Selectores en la barra lateral
    meses = sorted(df_raw["Mes_Año"].unique().tolist(), reverse=True)
    mes_sel = st.sidebar.selectbox("📅 Seleccionar Mes de Gestión", meses)
    
    df_mes = df_raw[df_raw["Mes_Año"] == mes_sel].copy()
    
except Exception as e:
    st.error("Error al conectar con los datos. Verificá el enlace del Google Sheet.")
    st.stop()

# --- 2. LÓGICA DE CONTROL DE ENTRENAMIENTOS ---
st.title(f"Control de Gestión: {mes_sel}")

tab1, tab2, tab3 = st.tabs(["🚀 Tablero de Objetivos", "💰 Caja y Cuotas", "📋 Detalle Histórico"])

with tab1:
    st.subheader("🏁 Estado de Sesiones Semanales")
    st.info("El sistema agrupa los gastos por semana y día para verificar el cumplimiento, sin importar el monto.")

    # Crear matriz de semanas (1 a 5)
    semanas_data = []
    for s in range(1, 6):
        # Filtrar gastos de esa semana para entrenamiento
        gastos_semana = df_mes[(df_mes["Semana_Mes"] == s) & (df_raw["Categoría"].str.contains("CANCHA|ENTRENAMIENTO", case=False, na=False))]
        
        martes = gastos_semana[gastos_semana["Dia_Nombre"] == "Tuesday"]["Monto"].sum()
        jueves = gastos_semana[gastos_semana["Dia_Nombre"] == "Thursday"]["Monto"].sum()
        torneo = df_mes[(df_mes["Semana_Mes"] == s) & (df_raw["Dia_Nombre"] == "Friday")]["Monto"].sum()
        
        semanas_data.append({
            "Semana": f"Semana {s}",
            "Martes (Entren.)": f"✅ ${martes:,.0f}" if martes > 0 else "❌ Pendiente",
            "Jueves (Entren.)": f"✅ ${jueves:,.0f}" if jueves > 0 else "❌ Pendiente",
            "Viernes (Torneo)": f"⚽ ${torneo:,.0f}" if torneo > 0 else "🏁 Sin Carga",
            "Total Semanal": martes + jueves + torneo
        })

    st.table(pd.DataFrame(semanas_data))

    # --- TERMÓMETROS DE GASTO ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        gasto_canchas = df_mes[df_raw["Categoría"].str.contains("CANCHA|ENTRENAMIENTO", case=False, na=False)]["Monto"].sum()
        st.write(f"**Inversión en Canchas:** ${gasto_canchas:,.0f}")
        # Estimamos 8 entrenamientos a 30k promedio
        progreso = min(gasto_canchas / 240000, 1.0) 
        st.progress(progreso)
        
    with col_b:
        gasto_torneo = df_mes[df_raw["Dia_Nombre"] == "Friday"]["Monto"].sum()
        st.write(f"**Inversión en Torneo:** ${gasto_torneo:,.0f}")
        progreso_t = min(gasto_torneo / 180000, 1.0)
        st.progress(progreso_t)

with tab2:
    # --- CÁLCULO DE INGRESOS ---
    ingresos_cuotas = df_mes[df_mes["Tipo de Movimiento"].str.contains("INGRESO", case=False, na=False)]["Monto"].sum()
    total_gastos = df_mes[df_mes["Tipo de Movimiento"].str.contains("GASTO", case=False, na=False)]["Monto"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Recaudación Mes", f"${ingresos_cuotas:,.0f}")
    col2.metric("Gastos Mes", f"${total_gastos:,.0f}")
    
    saldo_mes = ingresos_cuotas - total_gastos
    col3.metric("Balance Mensual", f"${saldo_mes:,.0f}", delta=f"{saldo_mes}")

    st.divider()
    st.subheader("Individual de Jugadores")
    # Aquí puedes integrar tu lista de jugadores_base y cruzarla con df_mes
    st.write("Cargando lista de pagos del mes seleccionado...")
    # (Lógica de cruce simplificada)
    pagos_jugadores = df_mes[df_mes["Tipo de Movimiento"] == "INGRESO"].groupby("Detalle / Nombre")["Monto"].sum().reset_index()
    st.dataframe(pagos_jugadores, use_container_width=True)

with tab3:
    st.subheader("Movimientos Crudos del Mes")
    st.dataframe(df_mes[["Fecha_DT", "Dia_Nombre", "Categoría", "Detalle / Nombre", "Monto"]], hide_index=True)
