import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

# --- 1. BASE DE DATOS FIJA (Tu memoria central) ---
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

# Nombres idénticos a los que pusiste en el menú desplegable del formulario
egresos_base = pd.DataFrame({
    "CONCEPTO": ["CAMISETAS", "INSCRIPCIÓN", "DT", "CANCHA ENTRENAMIENTO", "ÁRBITRO Y CANCHA (TORNEO)", "TERCER TIEMPO", "VARIOS (ACLARAR EN WHATSAPP)"],
    "COSTO ESTIMADO": [429000, 200000, 150000, 192000, 200000, 0, 0],
    "MONTO PAGADO": [214500, 0, 0, 0, 0, 0, 0]
})

# --- 2. CONEXIÓN AL FORMULARIO ---
sheet_url = "https://docs.google.com/spreadsheets/d/1S8O8ibkWjLofoS2JPPuZH3boQ88aKaY77a4fF0RSk5Y/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    
    # LIMPIEZA EXTREMA: Forzamos todo a mayúsculas y sin espacios para que no falle el cruce
    df.columns = df.columns.str.strip()
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
    
    df["Tipo de Movimiento"] = df["Tipo de Movimiento"].astype(str).str.strip().str.upper()
    df["Categoría"] = df["Categoría"].astype(str).str.strip().str.upper()
    df["Detalle / Nombre"] = df["Detalle / Nombre"].astype(str).str.strip().str.upper()
    
    # --- 3. EL CRUCE DE DATOS BLINDADO ---
    
    # A. Buscar ingresos de Sponsors
    ingresos_sponsors = df[(df["Tipo de Movimiento"] == "INGRESO") & (df["Categoría"].str.contains("SPONSOR", na=False))]
    for index, row in ingresos_sponsors.iterrows():
        nombre_form = row["Detalle / Nombre"]
        sponsors_base.loc[sponsors_base["SPONSOR"] == nombre_form, "MONTO INGRESADO"] += row["Monto"]

    # B. Buscar cuotas de Jugadores
    ingresos_jugadores = df[(df["Tipo de Movimiento"] == "INGRESO") & (df["Categoría"].str.contains("CUOTA", na=False))]
    for index, row in ingresos_jugadores.iterrows():
        nombre_form = row["Detalle / Nombre"]
        jugadores_base.loc[jugadores_base["JUGADOR"] == nombre_form, "ESTADO"] = "PAGO"

    # C. Buscar gastos y sumarlos al presupuesto
    gastos = df[df["Tipo de Movimiento"] == "GASTO"]
    for index, row in gastos.iterrows():
        nombre_gasto = row["Detalle / Nombre"]  # Ahora busca el gasto directo desde la lista desplegable
        egresos_base.loc[egresos_base["CONCEPTO"] == nombre_gasto, "MONTO PAGADO"] += row["Monto"]

except Exception as e:
    st.warning("El sistema está conectado, pero espera que se carguen movimientos compatibles.")


# --- 4. CÁLCULOS FINALES ---
sponsors_base["FALTA COBRAR"] = sponsors_base["TOTAL ACORDADO"] - sponsors_base["MONTO INGRESADO"]
egresos_base["FALTA PAGAR"] = egresos_base["COSTO ESTIMADO"] - egresos_base["MONTO PAGADO"]

total_ingresado = sponsors_base["MONTO INGRESADO"].sum() + (len(jugadores_base[jugadores_base["ESTADO"] == "PAGO"]) * 35000)
total_gastado = egresos_base["MONTO PAGADO"].sum()
saldo_caja = total_ingresado - total_gastado


# --- 5. DISEÑO DE LAS PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Caja", "📈 Sponsors", "📉 Gastos", "👕 Plantel", "📓 Historial"])

with tab1:
    st.header("Caja Real (Dinero en Mano)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Plata que Entró", f"${total_ingresado:,.0f}")
    col2.metric("Plata que Salió", f"${total_gastado:,.0f}")
    col3.metric("SALDO EN CAJA", f"${saldo_caja:,.0f}")
    
    st.divider()
    st.warning(f"⚠️ Plata en la calle (Falta cobrar de Sponsors): **${sponsors_base['FALTA COBRAR'].sum():,.0f}**")

with tab2:
    st.subheader("Estado de Sponsors")
    st.dataframe(sponsors_base, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Presupuesto de Gastos")
    st.dataframe(egresos_base, hide_index=True, use_container_width=True)

with tab4:
    st.subheader("Estado del Plantel")
    st.dataframe(jugadores_base.sort_values(by="DORSAL"), hide_index=True, use_container_width=True)

with tab5:
    st.subheader("Todos los movimientos (Desde Formulario)")
    if 'df' in locals():
        st.dataframe(df, hide_index=True, use_container_width=True)
