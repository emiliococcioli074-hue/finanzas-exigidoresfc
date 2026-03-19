import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

tab1, tab2, tab3, tab4 = st.tabs(["💰 Resumen", "📈 Ingresos", "📉 Egresos", "👕 Plantel"])

# --- CARGA DE DATOS ---

# Sponsors (Con el ingreso real de GAP Producciones)
sponsors_data = pd.DataFrame({
    "SPONSOR": ["GAP PRODUCCIONES", "ELICARS", "RAMA", "MATAFUEGOS SAN MIGUEL", "DILASCIO LEGALES"],
    "TOTAL ACORDADO": [300000, 200000, 100000, 100000, 100000],
    "MONTO INGRESADO": [214500, 0, 0, 0, 0] 
})
sponsors_data["FALTA COBRAR"] = sponsors_data["TOTAL ACORDADO"] - sponsors_data["MONTO INGRESADO"]
plata_real_sponsors = sponsors_data["MONTO INGRESADO"].sum()

# Jugadores (Todos pendientes por ahora)
jugadores_data = pd.DataFrame({
    "DORSAL": [1, 5, 8, 9, 10, 11, 12, 15, 19, 22, 26, 27, 33],
    "JUGADOR": ["ALVARO", "LUCAS", "RIOS", "ELIAS", "EMILIO", "IVAN", "MARCOS", "MIGUEL", "FELICE", "MOTHE", "JUAN X", "GABO", "CHARLY"],
    "ESTADO": ["PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE"] 
})
jugadores_al_dia = len(jugadores_data[jugadores_data["ESTADO"] == "PAGO"])
plata_real_cuotas = jugadores_al_dia * 35000

# Egresos (Con la seña de las camisetas)
egresos_data = pd.DataFrame({
    "CONCEPTO": ["CAMISETAS (Única vez)", "INSCRIPCIÓN (Única vez)", "DT (Mensual)", "CANCHA (Mensual)", "PARTIDOS (Semanal)"],
    "COSTO TOTAL": [429000, 200000, 150000, 180000, 50000],
    "MONTO PAGADO": [214500, 50000, 0, 0, 0] 
})
egresos_data["FALTA PAGAR"] = egresos_data["COSTO TOTAL"] - egresos_data["MONTO PAGADO"]
gastos_reales_pagados = egresos_data["MONTO PAGADO"].sum()


# --- DISEÑO DE LAS PESTAÑAS ---

with tab1:
    st.header("Caja Real (Dinero en Mano)")
    ingresos_reales_totales = plata_real_sponsors + plata_real_cuotas
    saldo_real = ingresos_reales_totales - gastos_reales_pagados
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Plata que Entró", f"${ingresos_reales_totales:,.0f}")
    col2.metric("Plata que Salió", f"${gastos_reales_pagados:,.0f}")
    col3.metric("SALDO EN CAJA", f"${saldo_real:,.0f}")
    
    st.divider()
    st.write("⚠️ **Alertas Financieras:**")
    st.warning(f"Plata en la calle (Falta cobrar de Sponsors): **${sponsors_data['FALTA COBRAR'].sum():,.0f}**")
    st.error(f"Deudas pendientes (Falta pagar de Gastos): **${egresos_data['FALTA PAGAR'].sum():,.0f}**")

with tab2:
    st.subheader("Estado de Sponsors")
    st.dataframe(sponsors_data, hide_index=True, use_container_width=True)
    st.info(f"Cuotas cobradas: {jugadores_al_dia} de 13 jugadores (**${plata_real_cuotas:,.0f}**)")

with tab3:
    st.subheader("Estado de Cuentas a Pagar")
    st.dataframe(egresos_data, hide_index=True, use_container_width=True)

with tab4:
    st.subheader("Lista de Jugadores")
    st.dataframe(jugadores_data.sort_values(by="DORSAL"), hide_index=True, use_container_width=True)