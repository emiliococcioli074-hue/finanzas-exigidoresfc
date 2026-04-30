import streamlit as st
import pandas as pd
import datetime
import calendar

st.set_page_config(page_title="Exigidores FC - Finanzas", page_icon="⚽", layout="wide")

# --- 0. CONFIGURACIÓN Y ESTILOS ---
CUOTA_MENSUAL = 41000

st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 10px; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. BASES DE DATOS FIJAS (Tus datos originales) ---
sponsors_base = pd.DataFrame({
    "SPONSOR": ["GAP PRODUCCIONES", "ELICARS", "RAMA", "MATAFUEGOS SAN MIGUEL", "DILASCIO LEGALES"],
    "TOTAL ACORDADO": [300000, 200000, 100000, 100000, 100000],
    "MONTO INGRESADO": [0, 0, 0, 0, 0] 
})

jugadores_base = pd.DataFrame({
    "DORSAL": [1, 5, 8, 9, 10, 11, 12, 15, 19, 22, 26, 27, 33],
    "JUGADOR": ["ALVARO", "LUCAS", "RIOS", "ELIAS", "EMILIO", "IVAN", "MARCOS", "MIGUEL", "FELICE", "MOTHE", "JUAN X", "GABO", "CHARLY"],
    "MONTO PAGADO": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
})

# --- 2. FUNCIONES DE APOYO ---
def get_week_of_month(date):
    first_day = date.replace(day=1)
    adjusted_dom = date.day + first_day.weekday()
    return int((adjusted_dom - 1) / 7) + 1

# --- 3. PROCESAMIENTO DE DATOS (Google Sheets) ---
sheet_url = "https://docs.google.com/spreadsheets/d/1gETPp5vu-tWJkMPSHRcrsl5XLuK3nKxtW5stVmO5y80/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    
    # Limpieza
    df["Monto"] = df["Monto"].replace('[\$,]', '', regex=True).astype(float).fillna(0)
    df["Tipo de Movimiento"] = df["Tipo de Movimiento"].str.upper()
    df["Detalle / Nombre"] = df["Detalle / Nombre"].astype(str).str.upper()
    df["Fecha_DT"] = pd.to_datetime(df["Marca temporal"], dayfirst=True)
    df["Mes_Año"] = df["Fecha_DT"].dt.strftime('%m-%Y')
    df["Dia_Nombre"] = df["Fecha_DT"].dt.day_name()
    df["Semana_Mes"] = df["Fecha_DT"].apply(get_week_of_month)

    # Selector de Mes (Principal)
    meses_disponibles = sorted(df["Mes_Año"].unique().tolist(), reverse=True)
    mes_seleccionado = st.sidebar.selectbox("📅 Mes de Gestión:", meses_disponibles)
    df_mensual = df[df["Mes_Año"] == mes_seleccionado]

except Exception as e:
    st.error(f"Error al conectar: {e}")
    st.stop()

# --- 4. CÁLCULOS DE CRUCE ---
# Sponsors (Histórico total)
for i, row in sponsors_base.iterrows():
    pago = df[(df["Tipo de Movimiento"] == "INGRESO") & (df["Detalle / Nombre"] == row["SPONSOR"])]["Monto"].sum()
    sponsors_base.at[i, "MONTO INGRESADO"] = pago

# Jugadores (Del mes seleccionado)
for i, row in jugadores_base.iterrows():
    pago = df_mensual[(df_mensual["Tipo de Movimiento"] == "INGRESO") & (df_mensual["Detalle / Nombre"] == row["JUGADOR"])]["Monto"].sum()
    jugadores_base.at[i, "MONTO PAGADO"] = pago

jugadores_base["DEUDA"] = CUOTA_MENSUAL - jugadores_base["MONTO PAGADO"]
jugadores_base["ESTADO"] = jugadores_base["MONTO PAGADO"].apply(lambda x: "✅ AL DÍA" if x >= CUOTA_MENSUAL else "❌ DEUDA")

# --- 5. INTERFAZ (TABS) ---
st.title("EXIGIDORES FC")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Inicio", "💸 Finanzas Semanales", "👕 Plantel", "📈 Sponsors", "⚽ Resultados"])

with tab1:
    col1, col2 = st.columns(2)
    total_ingresos = df[df["Tipo de Movimiento"] == "INGRESO"]["Monto"].sum()
    total_gastos = df[df["Tipo de Movimiento"] == "GASTO"]["Monto"].sum()
    saldo_total = total_ingresos - total_gastos
    
    col1.metric("Caja Fuerte (Total)", f"${saldo_total:,.0f}")
    col2.metric("Recaudación Mes", f"${df_mensual[df_mensual['Tipo de Movimiento'] == 'INGRESO']['Monto'].sum():,.0f}")

with tab2:
    st.subheader(f"📅 Control de Gastos: {mes_seleccionado}")
    st.write("Solo Martes (Entrenamiento) y Viernes (Torneo)")
    
    semanas_data = []
    for s in range(1, 6):
        # Filtramos por semana y categoría
        gastos_s = df_mensual[df_mensual["Semana_Mes"] == s]
        
        # Entrenamiento (Martes)
        monto_martes = gastos_s[(gastos_s["Dia_Nombre"] == "Tuesday") & 
                                (gastos_s["Categoría"].str.contains("CANCHA|ENTRENAMIENTO", na=False))]["Monto"].sum()
        # Torneo (Viernes)
        monto_viernes = gastos_s[(gastos_s["Dia_Nombre"] == "Friday")]["Monto"].sum()
        
        semanas_data.append({
            "Semana": f"Semana {s}",
            "Martes (Entren.)": f"✅ ${monto_martes:,.0f}" if monto_martes > 0 else "❌ Faltante",
            "Viernes (Torneo)": f"⚽ ${monto_viernes:,.0f}" if monto_viernes > 0 else "🏁 Sin Carga",
            "Total Semanal": monto_martes + monto_viernes
        })
    
    st.table(pd.DataFrame(semanas_data))
    
    # Gastos Varios del mes (que no son martes/viernes)
    st.subheader("Otros Gastos del Mes")
    otros = df_mensual[(df_mensual["Tipo de Movimiento"] == "GASTO") & 
                       (~df_mensual["Dia_Nombre"].isin(["Tuesday", "Friday"]))]
    st.dataframe(otros[["Fecha_DT", "Categoría", "Detalle / Nombre", "Monto"]], hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Estado de Cuotas")
    st.dataframe(jugadores_base.sort_values("DEUDA", ascending=False), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Sponsors (Acuerdos Anuales)")
    sponsors_base["PENDIENTE"] = sponsors_base["TOTAL ACORDADO"] - sponsors_base["MONTO INGRESADO"]
    st.dataframe(sponsors_base, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("⚽ Historial Deportivo")
    # Datos simulados o podés crear un DataFrame similar a sponsors_base si tenés los resultados
    resultados = pd.DataFrame({
        "FECHA": ["03/03/2026"],
        "RIVAL": ["LA AMERICA"],
        "GF": [4], "GC": [6],
        "RESULTADO": ["❌ Derrota"],
        "GOLEADORES": ["Gabo (2), Ivanchu, Emilio"]
    })
    st.dataframe(resultados, use_container_width=True, hide_index=True)
