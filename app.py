import streamlit as st
import pandas as pd
import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA (Optimizado para celulares)
st.set_page_config(page_title="VentaFácil VE", page_icon="📊", layout="centered")

# 2. SISTEMA DE SEGURIDAD Y CANDADO (Lógica de 3 días)
ARCHIVO_LICENCIA = ".licencia_control.txt"
CODIGO_SECRETO_ACTIVACION = "TACARIGUA2026"  # Este es el código que tú les venderás

def verificar_estado_licencia():
    # Si ya está activado permanentemente
    if os.path.exists(ARCHIVO_LICENCIA):
        with open(ARCHIVO_LICENCIA, "r") as f:
            contenido = f.read().strip()
            if contenido == "ACTIVADO_PERMANENTE":
                return "OK", 0

    # Si es la primera vez que se abre la app, creamos la fecha de instalación
    fecha_hoy = datetime.date.today()
    if not os.path.exists(ARCHIVO_LICENCIA):
        with open(ARCHIVO_LICENCIA, "w") as f:
            f.write(f"INSTALADO:{fecha_hoy.isoformat()}")
        return "PRUEBA", 3

    # Si ya existe, leemos cuándo se instaló
    with open(ARCHIVO_LICENCIA, "r") as f:
        linea = f.read().strip()
        
    if linea.startswith("INSTALADO:"):
        fecha_inst_str = linea.split(":")[1]
        fecha_instalacion = datetime.date.fromisoformat(fecha_inst_str)
        dias_transcurridos = (fecha_hoy - fecha_instalacion).days
        dias_restantes = 3 - dias_transcurridos
        
        if dias_restantes <= 0:
            return "BLOQUEADO", 0
        else:
            return "PRUEBA", dias_restantes
            
    return "BLOQUEADO", 0

def activar_app_permanente():
    with open(ARCHIVO_LICENCIA, "w") as f:
        f.write("ACTIVADO_PERMANENTE")

# Verificar el estado antes de cargar el Frontend
estado, dias_disponibles = verificar_estado_licencia()

# ----------------- CASO 1: APLICACIÓN BLOQUEADA -----------------
if estado == "BLOQUEADO":
    st.error("🚨 PERIODO DE PRUEBA VENCIDO")
    st.markdown("### Tu acceso gratuito de 3 días ha caducado.")
    st.write("Para obtener tu código de activación permanente y seguir usando la aplicación para ahorrar tiempo en tu negocio, comunícate con el desarrollador.")
    
    # Botón directo que simula enviar un mensaje a tu WhatsApp
    st.markdown("[📲 Solicitar código por WhatsApp](https://wa.me)")
    
    st.write("---")
    codigo_usuario = st.text_input("Introduce tu código de activación:", type="password")
    if st.button("🔓 Desbloquear Aplicación", use_container_width=True):
        if codigo_usuario == CODIGO_SECRETO_ACTIVACION:
            activar_app_permanente()
            st.success("🎉 ¡Aplicación activada con éxito para siempre! Por favor, refresca la página.")
            st.rerun()
        else:
            st.error("❌ Código incorrecto. Verifica o contacta al desarrollador.")

# ----------------- CASO 2: MODO PRUEBA O ACTIVADO -----------------
else:
    # Encabezado e información de días
    st.title("📊 VentaFácil VE")
    if estado == "PRUEBA":
        st.warning(f"⏳ Periodo de prueba activo: Te quedan {dias_disponibles} días de uso gratuito.")
    else:
        st.success("🔒 Versión Completa Activada ✅")
        
    st.write("---")

    # SECCIÓN 1: Tasa Cambiaria del Día
    st.markdown("### 💰 Tasa Cambiaria")
    tasa_dolar = st.number_input("Tasa del dólar del día (Bs.):", min_value=1.0, value=45.50, step=0.10)

    st.write("---")

    # SECCIÓN 2: Base de datos temporal en memoria (Listas y Diccionarios)
    if "inventario" not in st.session_state:
        st.session_state.inventario = []

    # Formulario de entrada de productos
    st.markdown("### 📦 Calcular y Registrar Producto")
    nombre_prod = st.text_input("Nombre del producto:", placeholder="Ej. Harina Pan 1kg")
    
    col1, col2 = st.columns(2)
    with col1:
        costo_usd = st.number_input("Costo de compra ($):", min_value=0.0, value=0.0, step=0.01)
    with col2:
        margen_ganancia = st.number_input("Margen de ganancia (%):", min_value=0.0, value=30.0, step=1.0)

    # Lógica al presionar el botón de calcular
    if st.button("➕ Calcular y Guardar", use_container_width=True):
        if nombre_prod and costo_usd > 0:
            # Fórmula comercial correcta: Costo * (1 + Margen / 100)
            precio_usd = costo_usd * (1 + (margen_ganancia / 100))
            precio_bs = precio_usd * tasa_dolar
            
            # Guardamos en la memoria (lista de diccionarios)
            st.session_state.inventario.append({
                "Producto": nombre_prod,
                "Costo ($)": f"{costo_usd:.2f}",
                "Ganancia (%)": f"{margen_ganancia:.0f}%",
                "Precio ($)": f"{precio_usd:.2f}",
                "Precio (Bs.)": f"{precio_bs:.2f}"
            })
            st.success(f"¡{nombre_prod} agregado con éxito!")
        else:
            st.error("⚠️ Introduce un nombre válido y un costo mayor a 0.")

    st.write("---")

    # SECCIÓN 3: Tabla de Resultados Dinámica
    st.markdown("### 📋 Lista de Precios Actualizada")
    if st.session_state.inventario:
        # Re-calculamos dinámicamente los precios en Bolívares si el usuario cambia la tasa
        inventario_actualizado = []
        for item in st.session_state.inventario:
            costo_num = float(item["Costo ($)"])
            margen_num = float(item["Ganancia (%)"].replace("%", ""))
            precio_usd_num = costo_num * (1 + (margen_num / 100))
            precio_bs_num = precio_usd_num * tasa_dolar
            
            inventario_actualizado.append({
                "Producto": item["Producto"],
                "Costo ($)": f"{costo_num:.2f} $",
                "Ganancia": item["Ganancia (%)"],
                "Precio ($)": f"{precio_usd_num:.2f} $",
                "Precio (Bs.)": f"{precio_bs_num:.2f} Bs."
            })
            
        df = pd.DataFrame(inventario_actualizado)
        st.dataframe(df, use_container_width=True)
        
        # Botón para limpiar la tabla
        if st.button("🗑️ Limpiar Inventario", use_container_width=True):
            st.session_state.inventario = []
            st.rerun()
    else:
        st.info("Aún no has registrado ningún producto hoy.")