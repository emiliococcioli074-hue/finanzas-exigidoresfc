import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Finanzas del Equipo", page_icon="⚽", layout="wide")

# --- 0. ENCABEZADO PERSONALIZADO ---
col_logo, col_nombre = st.columns([1, 6])
with col_logo:
    try:
        # Busca el archivo directamente en tu GitHub
        st.image("logo_equipo.jpeg", width=120)
    except:
        st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)

with col_nombre:
    st.markdown("<h1 style='margin-bottom: 0px;'>Exigidores FC FC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; font-size: 18px;'>Portal Oficial de Transparencia y Gestión</p>", unsafe_allow_html=True)

st.divider()

CUOTA_MENSUAL = 41000

# --- 1. BASE DE DATOS FIJA ---
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

egresos_base = pd.DataFrame({
    "CONCEPTO": ["CAMISETAS", "INSCRIPCIÓN", "DT", "CANCHA ENTRENAMIENTO", "ÁRBITRO Y CANCHA (TORNEO)", "TERCER TIEMPO", "VARIOS"],
    "COSTO ESTIMADO": [462500, 200000, 150000, 120000, 200000, 0, 0],
    "MONTO PAGADO": [462500, 50000, 0, 0, 0, 0, 0]
})

# --- 2. CONEXIÓN AL EXCEL DEL FORMULARIO ---
sheet_url = "https://docs.google.com/spreadsheets/d/1gETPp5vu-tWJkMPSHRcrsl5XLuK3nKxtW5stVmO5y80/export?format=csv"

def limpiar_monto(valor):
    valor = str(valor).replace("$", "").strip()
    if not valor or valor.lower() == 'nan': return 0.0
    if "," in valor and "." in valor: valor = valor.replace(".", "").replace(",", ".")
    elif "," in valor: valor = valor.replace(",", ".")
    return pd.to_numeric(valor, errors="coerce") or 0.0

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    
    df["Monto"] = df["Monto"].apply(limpiar_monto)
    df["Tipo de Movimiento"] = df["Tipo de Movimiento"].astype(str).str.strip().str.upper()
    df["Detalle / Nombre"] = df["Detalle / Nombre"].astype(str).str.strip().str.upper()
    df["Categoría"] = df["Categoría"].astype(str).str.strip().str.upper()

    df["Fecha Real"] = pd.to_datetime(df["Marca temporal"], dayfirst=True, errors="coerce")
    df["Mes_Año"] = df["Fecha Real"].dt.strftime('%m-%Y')
    
    meses_con_datos = df["Mes_Año"].dropna().unique().tolist()
    mes_actual_str = pd.Timestamp.now(tz='America/Argentina/Buenos_Aires').strftime('%m-%Y')
    if mes_actual_str not in meses_con_datos: meses_con_datos.append(mes_actual_str)
    meses_con_datos.sort(reverse=True)

    df_mensual = df[df["Mes_Año"] == mes_actual_str] 

    # --- 3. CRUCE INTELIGENTE ---
    for sponsor in sponsors_base["SPONSOR"]:
        mask = (df["Tipo de Movimiento"] == "INGRESO") & ((df["Detalle / Nombre"] == sponsor) | (df["Categoría"] == sponsor))
        sponsors_base.loc[sponsors_base["SPONSOR"] == sponsor, "MONTO INGRESADO"] = df[mask]["Monto"].sum()
        
    for jugador in jugadores_base["JUGADOR"]:
        plata = df_mensual[(df_mensual["Tipo de Movimiento"] == "INGRESO") & (df_mensual["Detalle / Nombre"] == jugador)]["Monto"].sum()
        jugadores_base.loc[jugadores_base["JUGADOR"] == jugador, "MONTO PAGADO"] = plata
            
    gastos_que_se_resetean = ["DT", "CANCHA ENTRENAMIENTO", "ÁRBITRO Y CANCHA (TORNEO)"]
    for gasto in egresos_base["CONCEPTO"]:
        if gasto in gastos_que_se_resetean:
            plata = df_mensual[(df_mensual["Tipo de Movimiento"] == "GASTO") & ((df_mensual["Detalle / Nombre"] == gasto) | (df_mensual["Categoría"] == gasto))]["Monto"].sum()
        else:
            plata = df[(df["Tipo de Movimiento"] == "GASTO") & ((df["Detalle / Nombre"] == gasto) | (df["Categoría"] == gasto))]["Monto"].sum()
        egresos_base.loc[egresos_base["CONCEPTO"] == gasto, "MONTO PAGADO"] = plata

except Exception as e:
    st.error(f"Esperando movimientos o revisando conexión: {e}")

# --- 4. CÁLCULOS FINALES ---
sponsors_base["FALTA COBRAR"] = sponsors_base["TOTAL ACORDADO"] - sponsors_base["MONTO INGRESADO"]
egresos_base["FALTA PAGAR"] = egresos_base["COSTO ESTIMADO"] - egresos_base["MONTO PAGADO"]

jugadores_base["DEUDA"] = CUOTA_MENSUAL - jugadores_base["MONTO PAGADO"]
jugadores_base.loc[jugadores_base["DEUDA"] < 0, "DEUDA"] = 0 

def estado_cuota(monto):
    if monto >= CUOTA_MENSUAL: return "AL DÍA ✅"
    elif monto > 0: return "PAGO PARCIAL ⏳"
    else: return "PENDIENTE ❌"

jugadores_base["ESTADO"] = jugadores_base["MONTO PAGADO"].apply(estado_cuota)

if 'df' in locals():
    saldo_caja_real = df[df["Tipo de Movimiento"].isin(["INGRESO", "SPONSOR"])]["Monto"].sum() - df[df["Tipo de Movimiento"] == "GASTO"]["Monto"].sum()
else:
    saldo_caja_real = 0

# --- 5. TABS DE NAVEGACIÓN ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Inicio", "💰 Finanzas", "👕 Plantel", "📈 Sponsors", "⚽ Resultados"])

with tab1:
    st.subheader("📊 Panel de Control")
    st.metric("Caja Fuerte Real (Histórica)", f"${saldo_caja_real:,.0f}")
    
    st.markdown("### 🗓️ Estado de Gastos Fijos (Mes Actual)")
    
    pago_cancha = egresos_base[egresos_base["CONCEPTO"] == "CANCHA ENTRENAMIENTO"]["MONTO PAGADO"].values[0]
    pago_torneo = egresos_base[egresos_base["CONCEPTO"] == "ÁRBITRO Y CANCHA (TORNEO)"]["MONTO PAGADO"].values[0]
    pago_dt = egresos_base[egresos_base["CONCEPTO"] == "DT"]["MONTO PAGADO"].values[0]

    colA, colB, colC = st.columns(3)
    
    with colA:
        st.info("🟢 **Cancha (Martes)**\n\nTope: $120.000")
        st.progress(min(pago_cancha / 120000, 1.0))
        st.write(f"Abonado: **${pago_cancha:,.0f}**")
        
    with colB:
        st.warning("🟡 **Árbitro (Viernes)**\n\nTope: $200.000")
        st.progress(min(pago_torneo / 200000, 1.0))
        st.write(f"Abonado: **${pago_torneo:,.0f}**")

    with colC:
        st.error("🔴 **DT (Mensual)**\n\nTope: $150.000")
        st.progress(min(pago_dt / 150000, 1.0))
        st.write(f"Abonado: **${pago_dt:,.0f}**")

with tab2:
    st.subheader("Movimientos Generales")
    st.write("Estado de pagos fijos y variables del equipo.")
    st.dataframe(egresos_base, hide_index=True, use_container_width=True)
    
    with st.expander("Ver Historial Completo"):
        if 'df' in locals():
            cols_mostrar = [c for c in df.columns if c not in ["Fecha Real", "Mes_Año"]]
            st.dataframe(df[cols_mostrar], hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Estado de Cuotas Mensuales")
    st.write(f"Mes en curso: **{mes_actual_str}** | Valor Cuota: **${CUOTA_MENSUAL:,.0f}**")
    
    # Ordenamos la tabla para que los que deben aparezcan primero
    tabla_limpia = jugadores_base[["DORSAL", "JUGADOR", "ESTADO", "MONTO PAGADO", "DEUDA"]].sort_values(by=["DEUDA", "DORSAL"], ascending=[False, True])
    
    st.dataframe(
        tabla_limpia,
        column_config={
            "MONTO PAGADO": st.column_config.NumberColumn(format="$%d"),
            "DEUDA": st.column_config.NumberColumn(format="$%d")
        },
        hide_index=True,
        use_container_width=True
    )

with tab4:
    st.subheader("Estado de Cuenta - Sponsors")
    st.dataframe(sponsors_base, hide_index=True, use_container_width=True)

with tab5:
    st.subheader("⚽ Historial Deportivo")
    st.write("Resumen de partidos y estadísticas del torneo.")
    
    # Datos de prueba hasta que vincules tu hoja de Excel
    resultados_simulados = pd.DataFrame({
        "FECHA": ["15/03/2026", "22/03/2026", "29/03/2026"],
        "RIVAL": ["Los Pumas", "El Ciclón", "La Máquina"],
        "GF": [3, 2, 0],
        "GC": [1, 2, 1],
        "RESULTADO": ["✅ Victoria", "➖ Empate", "❌ Derrota"],
        "GOLEADORES": ["Alvaro(2), Lucas", "Elias, Rios", "-"]
    })
    
    st.dataframe(resultados_simulados, hide_index=True, use_container_width=True)
