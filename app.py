import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# Configuración inicial de la página
st.set_page_config(page_title="Calculadora Cambiaria", page_icon="💰")

# --- MEMORIA DE LA APP (SESSION STATE) ---
# Inicializamos la lista de productos si no existe en la memoria de la sesión
if "lista_productos" not in st.session_state:
    st.session_state.lista_productos = []

# --- FUNCIÓN PARA OBTENER LAS TASAS EN TIEM realtime ---
@st.cache_data(ttl=3600)
def obtener_tasas_venezuela():
    try:
        url = "https://disweb.top"
        respuesta = requests.get(url, timeout=5).json()
        bcv = float(respuesta.get("bcv", {}).get("valor", 45.50))
        monitor = float(respuesta.get("enparalelovzla", {}).get("valor", 54.20))
        return bcv, monitor
    except Exception:
        # Valores de respaldo por si falla la API externa
        return 45.50, 54.20

tasa_bcv_hoy, tasa_monitor_hoy = obtener_tasas_venezuela()

# --- SECCIÓN 1: SELECCIÓN DE TASA CAMBIARIA ---
st.header("💰 Tasa Cambiaria")

tipo_tasa = st.selectbox(
    "Selecciona la tasa de referencia que deseas usar:",
    ["Dólar Oficial (BCV)", "Dólar Paralelo (Monitor)", "Introducir tasa manualmente"]
)

if tipo_tasa == "Dólar Oficial (BCV)":
    tasa_activa = st.number_input("Tasa del dólar BCV del día (Bs.):", value=tasa_bcv_hoy, disabled=True, format="%.2f")
elif tipo_tasa == "Dólar Paralelo (Monitor)":
    tasa_activa = st.number_input("Tasa del dólar Paralelo (Bs.):", value=tasa_monitor_hoy, disabled=True, format="%.2f")
else:
    tasa_activa = st.number_input("Introduce la tasa manual (Bs.):", value=45.50, step=0.10, format="%.2f")

st.write("---")

# --- SECCIÓN 2: CALCULAR Y REGISTRAR PRODUCTO ---
st.header("📦 Calcular y Registrar Producto")

nombre_producto = st.text_input("Nombre del producto:", value="Litro de gasolina")

col1, col2 = st.columns(2)
with col1:
    costo_compra = st.number_input("Costo de compra ($):", value=10.00, step=0.50, format="%.2f")
with col2:
    margen_ganancia = st.number_input("Margen de ganancia (%):", value=30.00, step=1.00, format="%.2f")

# --- BOTÓN DE ACCIÓN: CALCULAR Y GUARDAR ---
if st.button("➕ Calcular y Guardar", use_container_width=True):
    # Cálculos matemáticos
    precio_venta_usd = costo_compra * (1 + (margen_ganancia / 100))
    precio_venta_bs = precio_venta_usd * tasa_activa
    
    # Crear el diccionario con los datos del nuevo producto
    nuevo_producto = {
        "Producto": nombre_producto,
        "Costo ($)": f"{costo_compra:.2f}",
        "Margen (%)": f"{margen_ganancia:.2f}%",
        "Precio ($)": round(precio_venta_usd, 2),
        "Precio (Bs.)": round(precio_venta_bs, 2),
        "Tasa Usada": f"{tasa_activa:.2f} ({tipo_tasa})"
    }
    
    # Guardar en la memoria de la sesión (añadir a la lista)
    st.session_state.lista_productos.append(nuevo_producto)
    st.success(f"¡{nombre_producto} agregado con éxito!")

st.write("---")

# --- SECCIÓN 3: LISTA DE PRECIOS ACTUALIZADA ---
st.header("📋 Lista de Precios Actualizada")

if st.session_state.lista_productos:
    # Convertimos la lista de la memoria en una tabla estructurada (DataFrame)
    df = pd.DataFrame(st.session_state.lista_productos)
    
    # Mostramos la tabla interactiva en Streamlit
    st.dataframe(df, use_container_width=True)
    
    # --- FUNCIÓN PARA GENERAR EL ARCHIVO EXCEL EN MEMORIA ---
    def generar_excel(dataframe):
        salida = BytesIO()
        with pd.ExcelWriter(salida, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Precios')
        return salida.getvalue()
    
    excel_data = generar_excel(df)
    
    # Botón nativo para que el usuario descargue el Excel
    st.download_button(
        label="📥 Descargar Lista en Excel (.xlsx)",
        data=excel_data,
        file_name="lista_de_precios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # Botón para limpiar la lista si se desea empezar desde cero
    if st.button("🗑️ Borrar toda la lista"):
        st.session_state.lista_productos = []
        st.rerun()
else:
    st.info("Aún no has registrado ningún producto. Los productos que agregues aparecerán aquí arriba.")
