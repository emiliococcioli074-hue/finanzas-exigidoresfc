import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

# --- 1. BASE DE DATOS FIJA ---
sponsors_base = pd.DataFrame({
    "SPONSOR": ["GAP PRODUCCIONES", "ELICARS", "RAMA", "MATAFUEGOS SAN MIGUEL", "DILASCIO LEGALES"],
    "TOTAL ACORDADO": [300000, 200000, 100000, 100000, 100000],
    "MONTO INGRESADO": [0, 0, 0, 0, 0] 
})

jugadores_base = pd.DataFrame({
    "DORSAL": [1, 5, 8, 9, 10, 11, 12, 15, 19, 22, 26, 27, 33],
    "JUGADOR": ["ALVARO", "LUCAS", "RIOS", "ELIAS", "EMILIO", "IVAN", "MARCOS", "MIGUEL", "FELICE", "MOTHE", "JUAN X", "GABO", "CHARLY"],
    "ESTADO": ["PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE"]
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

    # ⏱️ MOTOR DE TIEMPO (NUEVO)
    df["Fecha Real"] = pd.to_datetime(df["Marca temporal"], dayfirst=True, errors="coerce")
    # Extraemos Mes y Año (Ej: "03-2026")
    df["Mes_Año"] = df["Fecha Real"].dt.strftime('%m-%Y')
    
    # Creamos el selector de meses para la pantalla
    meses_con_datos = df["Mes_Año"].dropna().unique().tolist()
    mes_actual_str = pd.Timestamp.now(tz='America/Argentina/Buenos_Aires').strftime('%m-%Y')
    
    if mes_actual_str not in meses_con_datos:
        meses_con_datos.append(mes_actual_str)
        
    # Ordenamos para que el más nuevo esté arriba
    meses_con_datos.sort(reverse=True)

    # Mostramos el selector en la aplicación
    st.write("### 📅 Filtrar por Mes de Gestión")
    mes_seleccionado = st.selectbox("Seleccioná el mes que querés analizar:", meses_con_datos)
    st.divider()

    # Separamos los datos: Todo el historial vs Solo el mes elegido
    df_mensual = df[df["Mes_Año"] == mes_seleccionado]

    # --- 3. CRUCE INTELIGENTE (Histórico vs Mensual) ---
    
    # SPONSORS (Histórico: Toda la plata que pusieron en el año)
    for sponsor in sponsors_base["SPONSOR"]:
        plata = df[(df["Tipo de Movimiento"] == "INGRESO") & (df["Detalle / Nombre"] == sponsor)]["Monto"].sum()
        sponsors_base.loc[sponsors_base["SPONSOR"] == sponsor, "MONTO INGRESADO"] = plata
        
    # JUGADORES (Mensual: Solo me importa si pagó ESTE MES seleccionado)
    for jugador in jugadores_base["JUGADOR"]:
        plata = df_mensual[(df_mensual["Tipo de Movimiento"] == "INGRESO") & (df_mensual["Detalle / Nombre"] == jugador)]["Monto"].sum()
        if plata > 0:
            jugadores_base.loc[jugadores_base["JUGADOR"] == jugador, "ESTADO"] = "PAGO"
            
    # GASTOS (Mixto: Camisetas es único, el resto se resetea)
    gastos_unicos = ["CAMISETAS", "INSCRIPCIÓN"]
    
    for gasto in egresos_base["CONCEPTO"]:
        if gasto in gastos_unicos:
            # Gasto Único: Suma todo el historial
            plata = df[(df["Tipo de Movimiento"] == "GASTO") & ((df["Detalle / Nombre"] == gasto) | (df["Categoría"] == gasto))]["Monto"].sum()
        else:
            # Gasto Recurrente (DT, Torneo, Cancha): Suma SOLO lo gastado ESTE MES
            plata = df_mensual[(df_mensual["Tipo de Movimiento"] == "GASTO") & ((df_mensual["Detalle / Nombre"] == gasto) | (df_mensual["Categoría"] == gasto))]["Monto"].sum()
            
        egresos_base.loc[egresos_base["CONCEPTO"] == gasto, "MONTO PAGADO"] = plata

except Exception as e:
    st.warning("El sistema está conectado, esperando movimientos.")

# --- 4. CÁLCULOS FINALES ---
sponsors_base["FALTA COBRAR"] = sponsors_base["TOTAL ACORDADO"] - sponsors_base["MONTO INGRESADO"]
egresos_base["FALTA PAGAR"] = egresos_base["COSTO ESTIMADO"] - egresos_base["MONTO PAGADO"]

# Para la CAJA REAL, usamos el flujo histórico de TODO el tiempo
if 'df' in locals():
    caja_historica_ingresos = df[df["Tipo de Movimiento"] == "INGRESO"]["Monto"].sum()
    caja_historica_gastos = df[df["Tipo de Movimiento"] == "GASTO"]["Monto"].sum()
    saldo_caja_real = caja_historica_ingresos - caja_historica_gastos
else:
    saldo_caja_real = 0

# Para el balance mensual, usamos solo la plata del mes
if 'df_mensual' in locals():
    ingreso_mes = df_mensual[df_mensual["Tipo de Movimiento"] == "INGRESO"]["Monto"].sum()
    gasto_mes = df_mensual[df_mensual["Tipo de Movimiento"] == "GASTO"]["Monto"].sum()
    saldo_mes = ingreso_mes - gasto_mes


# --- 5. DISEÑO DE LAS PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Caja General", "📉 Gastos del Mes", "👕 Plantel (Cuotas)", "📈 Sponsors (Anual)", "📓 Historial"])

with tab1:
    st.header("Caja Fuerte (Dinero Real Guardado)")
    st.metric("SALDO ACTUAL (Todo el año)", f"${saldo_caja_real:,.0f}")
    
    st.divider()
    
    if 'df_mensual' in locals():
        st.subheader(f"Balance de {mes_seleccionado}")
        st.write("Cómo venimos operativamente este mes:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Recaudado este mes", f"${ingreso_mes:,.0f}")
        col2.metric("Gastado este mes", f"${gasto_mes:,.0f}")
        col3.metric("Saldo del mes", f"${saldo_mes:,.0f}")

with tab2:
    st.subheader(f"Presupuesto Operativo ({mes_seleccionado})")
    st.write("Camisetas e Inscripción muestran el acumulado de todo el año. El resto se resetea a cero cada mes.")
    st.dataframe(egresos_base, hide_index=True, use_container_width=True)

with tab3:
    st.subheader(f"Estado de Cuotas ({mes_seleccionado})")
    st.write("Jugadores que pagaron la cuota en el mes seleccionado.")
    st.dataframe(jugadores_base.sort_values(by="DORSAL"), hide_index=True, use_container_width=True)

with tab4:
    st.subheader("Estado de Sponsors (Todo el año)")
    st.dataframe(sponsors_base, hide_index=True, use_container_width=True)

with tab5:
    st.subheader("Todos los movimientos (Desde Formulario)")
    if 'df' in locals():
        # Ocultamos las columnas internas de cálculo de fecha
        cols_mostrar = [c for c in df.columns if c not in ["Fecha Real", "Mes_Año"]]
        st.dataframe(df[cols_mostrar], hide_index=True, use_container_width=True)
