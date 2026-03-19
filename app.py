import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="centered")
st.title("⚽ Gestión del Equipo")

# --- CONEXIÓN A GOOGLE SHEETS (TU BÓVEDA) ---
# Este es tu link transformado mágicamente a CSV para que Python lo lea
sheet_url = "https://docs.google.com/spreadsheets/d/1S8O8ibkWjLofoS2JPPuZH3boQ88aKaY77a4fF0RSk5Y/export?format=csv"

try:
    # Leemos los datos en vivo
    df = pd.read_csv(sheet_url)
    
    # Limpiamos un poco los nombres de las columnas por si tienen espacios
    df.columns = df.columns.str.strip()
    
    # Nos aseguramos de que la columna Monto sea numérica (y si está vacía, le ponemos 0)
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)

except Exception as e:
    st.error("⚠️ Todavía no hay datos cargados o hay un problema leyendo el Excel. Cargá el primer pago en tu Formulario para inicializar el sistema.")
    st.stop()

# --- CÁLCULOS AUTOMÁTICOS ---
# Separamos la plata que entra de la plata que sale
ingresos = df[df["Tipo de Movimiento"] == "Ingreso"]
gastos = df[df["Tipo de Movimiento"] == "Gasto"]

total_ingresos = ingresos["Monto"].sum()
total_gastos = gastos["Monto"].sum()
saldo_caja = total_ingresos - total_gastos

# --- DISEÑO DE LAS PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["💰 Resumen General", "📈 Ingresos", "📉 Gastos", "📓 Historial de Movimientos"])

with tab1:
    st.header("Caja Real (Dinero en Mano)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Plata que Entró", f"${total_ingresos:,.0f}")
    col2.metric("Plata que Salió", f"${total_gastos:,.0f}")
    
    # Mostramos el saldo en verde si es positivo, o en rojo si estamos en deuda
    if saldo_caja >= 0:
        col3.metric("SALDO EN CAJA", f"${saldo_caja:,.0f}")
    else:
        col3.metric("SALDO EN CAJA", f"${saldo_caja:,.0f}", "- EN ROJO")
    
    st.divider()
    
    # Un gráfico de torta rápido para ver en qué se nos va la plata
    if not gastos.empty:
        st.subheader("¿En qué gastamos la plata?")
        gastos_agrupados = gastos.groupby("Categoría")["Monto"].sum().reset_index()
        st.bar_chart(gastos_agrupados.set_index("Categoría"))

with tab2:
    st.subheader("Detalle de Ingresos")
    if ingresos.empty:
        st.info("No hay ingresos registrados todavía.")
    else:
        # Agrupamos por categoría (Sponsors vs Cuotas)
        resumen_ingresos = ingresos.groupby("Categoría")["Monto"].sum().reset_index()
        st.dataframe(resumen_ingresos, hide_index=True, use_container_width=True)
        
        st.write("**Detalle uno por uno:**")
        st.dataframe(ingresos[["Marca temporal", "Categoría", "Detalle / Nombre", "Monto"]], hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Detalle de Gastos")
    if gastos.empty:
        st.info("No hay gastos registrados todavía.")
    else:
        # Agrupamos por categoría (Cancha, DT, Torneo, etc)
        resumen_gastos = gastos.groupby("Categoría")["Monto"].sum().reset_index()
        st.dataframe(resumen_gastos, hide_index=True, use_container_width=True)
        
        st.write("**Detalle uno por uno:**")
        st.dataframe(gastos[["Marca temporal", "Categoría", "Detalle / Nombre", "Monto"]], hide_index=True, use_container_width=True)

with tab4:
    st.subheader("El Libro Diario (Todos los movimientos)")
    st.write("Acá se ve todo lo que cargás en el formulario, ordenado del más viejo al más nuevo.")
    # Mostramos el Excel crudo pero lindo
    st.dataframe(df, hide_index=True, use_container_width=True)
