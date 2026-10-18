import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
import datetime

# Configurar la página para que se vea bien en móviles
st.set_page_config(page_title="Registro de Personal", layout="centered")

# 1. Conectar a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer la base de datos de personal (Hoja 'Personal')
# Asegúrate de poner la URL de tu Google Sheet aquí en un archivo de configuración (secrets) o directamente en la conexión.
df_personal = conn.read(worksheet="Personal", ttl=0) # ttl=0 fuerza a leer siempre los datos más recientes

st.title("📝 Formulario de Registro")

# 2. Lógica de selección de Sucursal y filtrado
sucursales_unicas = df_personal["Sucursal"].dropna().unique().tolist()
sucursal_seleccionada = st.selectbox("Seleccione la Sucursal:", [""] + sucursales_unicas)

if sucursal_seleccionada:
    # Filtrar nombres basados en la sucursal
    df_filtrado = df_personal[df_personal["Sucursal"] == sucursal_seleccionada]
    nombres_disponibles = df_filtrado["Nombre y Apellido"].tolist()
    
    nombre_seleccionado = st.selectbox("Seleccione el empleado:", [""] + nombres_disponibles)
    
    if nombre_seleccionado:
        # 3. Resto del formulario
        edad = st.number_input("Edad:", min_value=18, max_value=100, step=1)
        comentarios = st.text_area("Comentarios:")
        
        st.write("📍 **Ubicación GPS** (Por favor permite el acceso al navegador)")
        # Componente para capturar GPS
        ubicacion = streamlit_geolocation()
        
        # Botón de enviar
        if st.button("Guardar Registro"):
            if ubicacion['latitude'] is not None:
                # Preparar los datos a guardar
                nuevo_registro = pd.DataFrame([{
                    "Sucursal": sucursal_seleccionada,
                    "Nombre y Apellido": nombre_seleccionado,
                    "Edad": edad,
                    "Comentarios": comentarios,
                    "Latitud": ubicacion['latitude'],
                    "Longitud": ubicacion['longitude'],
                    "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                
                # Leer la hoja de registros actual
                df_registros = conn.read(worksheet="Registros", ttl=0)
                
                # Unir el nuevo registro y actualizar el Google Sheet
                df_actualizado = pd.concat([df_registros, nuevo_registro], ignore_index=True)
                conn.update(worksheet="Registros", data=df_actualizado)
                
                st.success("¡Registro guardado con éxito!")
            else:
                st.error("Por favor, haz clic en el botón de ubicación para obtener las coordenadas antes de guardar.")