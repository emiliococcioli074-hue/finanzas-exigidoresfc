import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

# --- 1. BASE DE DATOS FIJA (Tu memoria central) ---
sponsors_base = pd.DataFrame({
    "SPONSOR": ["GAP PRODUCCIONES", "ELICARS", "RAMA", "MATAFUEGOS SAN MIGUEL", "DILASCIO LEGALES"],
    "TOTAL ACORDADO": [300000, 200000, 100000, 100000, 100000],
    "MONTO INGRESADO": [0, 0, 0, 0, 0] # Arrancan en cero, se llenan solos con el Formulario
})

jugadores_base = pd.DataFrame({
    "DORSAL": [1, 5, 8, 9, 10, 11, 12, 15, 19, 22, 26, 27, 33],
    "JUGADOR": ["ALVARO", "LUCAS", "RIOS", "ELIAS", "EMILIO", "IVAN", "MARCOS", "MIGUEL", "FELICE", "MOTHE", "JUAN X", "GABO", "CHARLY"],
    "ESTADO": ["PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE"]
})

egresos_base = pd.DataFrame({
    "CONCEPTO": ["CAMISETAS", "INSCRIPCIÓN", "DT", "CANCHA ENTRENAMIENTO", "FECHA DE TORNEO", "TERCER TIEMPO", "OTROS GASTOS"],
    "COSTO ESTIMADO": [429000, 200000, 150000, 192000, 200000, 0, 0],
    "MONTO PAGADO": [0, 0, 0, 0, 0, 0, 0]
})

# --- 2. CONEXIÓN AL FORMULARIO (Tu Cajero) ---
sheet_url = "https://docs.google.com/spreadsheets/d/1S8O8ibkWjLofoS2JPPuZH3boQ88aKaY77a4fF0RSk5Y/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
    
    # --- 3. EL CRUCE DE DATOS MÁGICO ---
    
    # A. Buscar ingresos de Sponsors y sumarlos a la lista
    ingresos_sponsors = df[(df["Tipo de Movimiento"] == "Ingreso") & (df["Categoría"] == "Sponsor")]
    for index, row in ingresos_sponsors.iterrows():
        nombre_form = str(row["Detalle / Nombre"]).strip().upper()
        # Buscamos quién es y le sumamos la plata
        sponsors_base.loc[sponsors_base["SPONSOR"].str.contains(nombre_form, na=False), "MONTO INGRESADO"] += row["Monto"]

    # B. Buscar cuotas y poner en "PAGO" a los jugadores
    ingresos_jugadores = df[(df["Tipo de Movimiento"] == "Ingreso") & (df["Categoría"] == "Cuota Mensual")]
    for index, row in ingresos_jugadores.iterrows():
        nombre_form = str(row["Detalle / Nombre"]).strip().upper()
        jugadores_base.loc[jugadores_base["JUGADOR"].str.contains(nombre_form, na=False), "ESTADO"] = "PAGO"

    # C. Buscar gastos y sumarlos al presupuesto
    gastos = df[df["Tipo de Movimiento"] == "Gasto"]
    for index, row in gastos.iterrows():
        categoria_form = str(row["Categoría"]).strip().upper()
        egresos_base.loc[egresos_base["CONCEPTO"] == categoria_form, "MONTO PAGADO"] += row["Monto"]

except Exception as e:
    st.warning("El historial está esperando nuevos movimientos.")


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
