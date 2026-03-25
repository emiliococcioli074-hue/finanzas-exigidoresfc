import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

CUOTA_MENSUAL = 41000

# --- 1. BASE DE DATOS FIJA ---
sponsors_base = pd.DataFrame({
    "SPONSOR": ["GAP PRODUCCIONES", "ELICARS", "RAMA", "MATAFUEGOS SAN MIGUEL", "DILASCIO LEGALES"],
    "TOTAL ACORDADO": [300000, 200000, 100000, 100000, 100000],
    "MONTO INGRESADO": [0, 0, 0, 0, 0] 
})

# Ahora los jugadores arrancan con 0 pesos pagados en vez de un "Estado" fijo
jugadores_base = pd.DataFrame({
    "DORSAL": [1, 5, 8, 9, 10, 11, 12, 15, 19, 22, 26, 27, 33],
    "JUGADOR": ["ALVARO", "LUCAS", "RIOS", "ELIAS", "EMILIO", "IVAN", "MARCOS", "MIGUEL", "FELICE", "MOTHE", "JUAN X", "GABO", "CHARLY"],
    "MONTO PAGADO": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
})

egresos_base = pd.DataFrame({
    "CONCEPTO": ["CAMISETAS", "INSCRIPCIÓN", "DT", "CANCHA ENTRENAMIENTO", "ÁRBITRO Y CANCHA (TORNEO)", "TERCER TIEMPO", "VARIOS (ACLARAR EN WHATSAPP)"],
    "COSTO ESTIMADO": [429000, 200000, 150000, 192000, 200000, 0, 0],
    "MONTO PAGADO": [0, 0, 0, 0, 0, 0, 0]
})

# --- 2. CONEXIÓN AL FORMULARIO ---
sheet_url = "https://docs.google.com/spreadsheets/d/1S8O8ibkWjLofoS2JPPuZH3boQ88aKaY77a4fF0RSk5Y/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    
    # Limpieza de montos y textos
    df["Monto"] = df["Monto"].astype(str).str.replace("$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
    
    df["Tipo de Movimiento"] = df["Tipo de Movimiento"].astype(str).str.strip().str.upper()
    df["Detalle / Nombre"] = df["Detalle / Nombre"].astype(str).str.strip().str.upper()
    df["Categoría"] = df["Categoría"].astype(str).str.strip().str.upper()

    # ⏱️ MOTOR DE TIEMPO
    df["Fecha Real"] = pd.to_datetime(df["Marca temporal"], dayfirst=True, errors="coerce")
    df["Mes_Año"] = df["Fecha Real"].dt.strftime('%m-%Y')
    
    # Selector de meses
    meses_con_datos = df["Mes_Año"].dropna().unique().tolist()
    mes_actual_str = pd.Timestamp.now(tz='America/Argentina/Buenos_Aires').strftime('%m-%Y')
    
    if mes_actual_str not in meses_con_datos:
        meses_con_datos.append(mes_actual_str)
        
    meses_con_datos.sort(reverse=True)

    st.write("### 📅 Filtrar por Mes de Gestión")
    mes_seleccionado = st.selectbox("Seleccioná el mes que querés analizar:", meses_con_datos)
    st.divider()

    df_mensual = df[df["Mes_Año"] == mes_seleccionado]

    # --- 3. CRUCE INTELIGENTE ---
    
    # SPONSORS (Histórico)
    for sponsor in sponsors_base["SPONSOR"]:
        plata = df[(df["Tipo de Movimiento"] == "INGRESO") & (df["Detalle / Nombre"] == sponsor)]["Monto"].sum()
        sponsors_base.loc[sponsors_base["SPONSOR"] == sponsor, "MONTO INGRESADO"] = plata
        
    # JUGADORES (Mensual - Sumamos toda la plata que entregaron este mes)
    for jugador in jugadores_base["JUGADOR"]:
        plata = df_mensual[(df_mensual["Tipo de Movimiento"] == "INGRESO") & (df_mensual["Detalle / Nombre"] == jugador)]["Monto"].sum()
        jugadores_base.loc[jugadores_base["JUGADOR"] == jugador, "MONTO PAGADO"] = plata
            
    # GASTOS: Reseteo inteligente
    gastos_que_se_resetean = ["DT", "CANCHA ENTRENAMIENTO", "ÁRBITRO Y CANCHA (TORNEO)"]
    
    for gasto in egresos_base["CONCEPTO"]:
        if gasto in gastos_que_se_resetean:
            plata = df_mensual[(df_mensual["Tipo de Movimiento"] == "GASTO") & ((df_mensual["Detalle / Nombre"] == gasto) | (df_mensual["Categoría"] == gasto))]["Monto"].sum()
        else:
            plata = df[(df["Tipo de Movimiento"] == "GASTO") & ((df["Detalle / Nombre"] == gasto) | (df["Categoría"] == gasto))]["Monto"].sum()
            
        egresos_base.loc[egresos_base["CONCEPTO"] == gasto, "MONTO PAGADO"] = plata

except Exception as e:
    st.warning("El sistema está conectado, esperando movimientos.")

# --- 4. CÁLCULOS FINALES ---
sponsors_base["FALTA COBRAR"] = sponsors_base["TOTAL ACORDADO"] - sponsors_base["MONTO INGRESADO"]
egresos_base["FALTA PAGAR"] = egresos_base["COSTO ESTIMADO"] - egresos_base["MONTO PAGADO"]

# Cálculo de Cuotas de Jugadores
jugadores_base["DEUDA"] = CUOTA_MENSUAL - jugadores_base["MONTO PAGADO"]
jugadores_base.loc[jugadores_base["DEUDA"] < 0, "DEUDA"] = 0 # Si alguien paga de más, la deuda no es negativa

# Función para ponerle la etiqueta automática a cada jugador
def estado_cuota(monto):
    if monto >= CUOTA_MENSUAL:
        return "AL DÍA ✅"
    elif monto > 0:
        return "PAGO PARCIAL ⏳"
    else:
        return "PENDIENTE ❌"

jugadores_base["ESTADO"] = jugadores_base["MONTO PAGADO"].apply(estado_cuota)

# Cálculos de Caja General
if 'df' in locals():
    caja_historica_ingresos = df[df["Tipo de Movimiento"] == "INGRESO"]["Monto"].sum()
    caja_historica_gastos = df[df["Tipo de Movimiento"] == "GASTO"]["Monto"].sum()
    saldo_caja_real = caja_historica_ingresos - caja_historica_gastos
else:
    saldo_caja_real = 0

if 'df_mensual' in locals():
    ingreso_mes = df_mensual[df_mensual["Tipo de Movimiento"] == "INGRESO"]["Monto"].sum()
    gasto_mes = df_mensual[df_mensual["Tipo de Movimiento"] == "GASTO"]["Monto"].sum()
    saldo_mes = ingreso_mes - gasto_mes


# --- 5. DISEÑO DE LAS PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Caja General", "📉 Gastos", "👕 Plantel", "📈 Sponsors", "📓 Historial"])

with tab1:
    st.header("Caja Fuerte (Dinero Real Guardado)")
    st.metric("SALDO ACTUAL (Todo el año)", f"${saldo_caja_real:,.0f}")
    
    st.divider()
    
    if 'df_mensual' in locals():
        st.subheader(f"Balance de {mes_seleccionado}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Recaudado este mes", f"${ingreso_mes:,.0f}")
        col2.metric("Gastado este mes", f"${gasto_mes:,.0f}")
        col3.metric("Resultado del mes", f"${saldo_mes:,.0f}")

with tab2:
    st.subheader(f"Estado de Gastos al mes de {mes_seleccionado}")
    st.write("DT y Canchas se resetean mensualmente. El resto acumula el total histórico.")
    st.dataframe(egresos_base, hide_index=True, use_container_width=True)

with tab3:
    st.subheader(f"Estado de Cuotas ({mes_seleccionado})")
    st.write(f"Valor de la cuota mensual: **${CUOTA_MENSUAL:,.0f}**")
    
    # Ordenamos la tabla para ver primero a los que deben y al final a los que están al día
    st.dataframe(jugadores_base.sort_values(by=["DEUDA", "DORSAL"], ascending=[False, True]), hide_index=True, use_container_width=True)

with tab4:
    st.subheader("Estado de Sponsors (Todo el año)")
    st.dataframe(sponsors_base, hide_index=True, use_container_width=True)

with tab5:
    st.subheader("Todos los movimientos (Desde Formulario)")
    if 'df' in locals():
        cols_mostrar = [c for c in df.columns if c not in ["Fecha Real", "Mes_Año"]]
        st.dataframe(df[cols_mostrar], hide_index=True, use_container_width=True)
