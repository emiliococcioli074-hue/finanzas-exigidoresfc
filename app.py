import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Resumen", "📈 Ingresos", "📉 Egresos", "👕 Plantel", "📅 Proyección"])

# --- CARGA DE DATOS ---

# Sponsors
sponsors_data = pd.DataFrame({
    "SPONSOR": ["GAP PRODUCCIONES", "ELICARS", "RAMA", "MATAFUEGOS SAN MIGUEL", "DILASCIO LEGALES"],
    "TOTAL ACORDADO": [300000, 200000, 100000, 100000, 100000],
    "MONTO INGRESADO": [214500, 0, 0, 0, 0] 
})
sponsors_data["FALTA COBRAR"] = sponsors_data["TOTAL ACORDADO"] - sponsors_data["MONTO INGRESADO"]
plata_real_sponsors = sponsors_data["MONTO INGRESADO"].sum()

# Jugadores
jugadores_data = pd.DataFrame({
    "DORSAL": [1, 5, 8, 9, 10, 11, 12, 15, 19, 22, 26, 27, 33],
    "JUGADOR": ["ALVARO", "LUCAS", "RIOS", "ELIAS", "EMILIO", "IVAN", "MARCOS", "MIGUEL", "FELICE", "MOTHE", "JUAN X", "GABO", "CHARLY"],
    "CUOTA": ["PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE", "PENDIENTE"] 
})
jugadores_al_dia = len(jugadores_data[jugadores_data["ESTADO"] == "PAGO"])
plata_real_cuotas = jugadores_al_dia * 35000

# Egresos (Actualizado con Cancha a $48.000 x 4 semanas)
egresos_data = pd.DataFrame({
    "CONCEPTO": ["CAMISETAS (Única vez)", "INSCRIPCIÓN (Única vez)", "DT (Mensual)", "CANCHA (4 x $48.000)", "PARTIDOS (4 x $50.000)"],
    "COSTO TOTAL": [429000, 200000, 150000, 192000, 200000],
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

with tab5:
    st.header("Proyección de Caja (Próximo Mes)")
    st.write("Cómo se va a consumir el dinero semana a semana para no quedar en rojo.")
    
    # Simulador del mes con Cancha Semanal
    proyeccion_data = pd.DataFrame({
        "Semana": ["Semana 1", "Semana 2", "Semana 3", "Semana 4"],
        "Ingresos (Cuotas)": [455000, 0, 0, 0],
        "DT (Mensual)": [-150000, 0, 0, 0],
        "Cancha (Semanal)": [-48000, -48000, -48000, -48000],
        "Partidos (Semanal)": [-50000, -50000, -50000, -50000]
    })
    
    # Calculamos el flujo de cada semana sumando todas las columnas
    proyeccion_data["Flujo Neto"] = proyeccion_data["Ingresos (Cuotas)"] + proyeccion_data["DT (Mensual)"] + proyeccion_data["Cancha (Semanal)"] + proyeccion_data["Partidos (Semanal)"]
    
    # Calculamos cuánta plata queda en el bolsillo al final de cada semana
    proyeccion_data["Bolsillo (Acumulado)"] = proyeccion_data["Flujo Neto"].cumsum()
    
    # 1. Mostramos el gráfico visual (la escalera que va bajando)
    st.subheader("Evolución del dinero en el mes")
    st.line_chart(proyeccion_data, x="Semana", y="Bolsillo (Acumulado)", color="#FF4B4B")
    
    # 2. Mostramos la tabla detallada
    st.dataframe(proyeccion_data, hide_index=True, use_container_width=True)
    
    # 3. Alerta de déficit real
    st.error(f"⚠️ Alerta: El ingreso por cuotas ($455.000) no llega a cubrir los gastos operativos del mes ($542.000). Déficit mensual: **${proyeccion_data['Flujo Neto'].sum():,.0f}**. Se debe cubrir con fondo de sponsors.")
