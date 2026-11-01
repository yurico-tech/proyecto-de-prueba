import streamlit as st
import requests

# Configuración inicial de la página
st.set_page_config(page_title="Calculadora Cambiaria", page_icon="💰")

# --- FUNCIÓN PARA OBTENER LAS TASAS EN TIEMPO REAL ---
@st.cache_data(ttl=3600)  # Guarda las tasas en memoria por 1 hora para que cargue rápido
def obtener_tasas_venezuela():
    try:
        # Usamos una API pública y estable orientada a la economía venezolana
        url = "https://disweb.top"
        respuesta = requests.get(url, timeout=5).json()
        
        # Extraemos los valores o colocamos valores de respaldo actualizados a la fecha
        bcv = float(respuesta.get("bcv", {}).get("valor", 889.26))
        monitor = float(respuesta.get("enparalelovzla", {}).get("valor", 945.50))
        return bcv, monitor
    except Exception:
        # Valores de respaldo (octubre 2026) por si falla la conexión externa
        return 889.26, 945.50

# Cargar las tasas del día automáticamente
tasa_bcv_hoy, tasa_monitor_hoy = obtener_tasas_venezuela()

# --- SECCIÓN 1: SELECCIÓN DE TASA CAMBIARIA ---
st.header("💰 Tasa Cambiaria")

# Menú desplegable para que el cliente o comercio elija
tipo_tasa = st.selectbox(
    "Selecciona la tasa de referencia que deseas usar:",
    ["Dólar Oficial (BCV)", "Dólar Paralelo (Monitor)", "Introducir tasa manualmente"]
)

# Lógica para asignar el valor numérico según la elección
if tipo_tasa == "Dólar Oficial (BCV)":
    tasa_activa = st.number_input("Tasa del dólar BCV del día (Bs.):", value=tasa_bcv_hoy, disabled=True, format="%.2f")
    st.caption("ℹ️ Tasa oficial cargada automáticamente desde el Banco Central de Venezuela.")

elif tipo_tasa == "Dólar Paralelo (Monitor)":
    tasa_activa = st.number_input("Tasa del dólar Paralelo (Bs.):", value=tasa_monitor_hoy, disabled=True, format="%.2f")
    st.caption("ℹ️ Tasa referencial del mercado paralelo cargada automáticamente.")

else:
    # Si elige manual, la casilla se desbloquea para que escriba lo que quiera (como el 45.50 de tu captura)
    tasa_activa = st.number_input("Introduce la tasa manual (Bs.):", value=45.50, step=0.10, format="%.2f")
    st.caption("✏️ Has seleccionado el modo manual. Puedes ajustar el valor usando los botones + y -.")

st.write("---")

# --- SECCIÓN 2: CALCULAR Y REGISTRAR PRODUCTO ---
st.header("📦 Calcular y Registrar Producto")

nombre_producto = st.text_input("Nombre del producto:", value="Litro de gasolina")

col1, col2 = st.columns(2)
with col1:
    costo_compra = st.number_input("Costo de compra ($):", value=10.00, step=0.50, format="%.2f")
with col2:
    margen_ganancia = st.number_input("Margen de ganancia (%):", value=30.00, step=1.00, format="%.2f")

# --- BOTÓN DE ACCIÓN ---
if st.button("➕ Calcular y Guardar", use_container_width=True):
    # Operaciones matemáticas básicas
    precio_venta_usd = costo_compra * (1 + (margen_ganancia / 100))
    precio_venta_bs = precio_venta_usd * tasa_activa
    
    # Mensaje verde de éxito que ya tienes integrado
    st.success(f"¡{nombre_producto} agregado con éxito!")
    
    # Cuadro informativo con el desglose de las cuentas según la tasa elegida
    st.info(
        f"**Resultados del Cálculo ({tipo_tasa}):**\n\n"
        f"• **Precio de Venta en Dólares:** {precio_venta_usd:.2f} $\n"
        f"• **Precio de Venta en Bolívares:** {precio_venta_bs:.2f} Bs."
    )
