import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
import time

# Configuración de la página
st.set_page_config(
    page_title="Rastreador GPS Educativo",
    page_icon="📍",
    layout="wide"
)

# Título y descripción
st.title("📍 Mi Ubicación en Tiempo Real")
st.markdown("""
**📖 App educativa** – Obtén y visualiza tu ubicación GPS actual en un mapa interactivo.  
**🔒 Privacidad** – La ubicación solo se muestra a ti, no se almacena ni se comparte.
""")

# Campo para número de teléfono (solo demostrativo)
phone = st.text_input("📞 Tu número de WhatsApp o móvil", value="+573052632705")

# Inicializar estado de sesión
if "location" not in st.session_state:
    st.session_state.location = None

# Botón principal
if st.button("📍 Obtener mi ubicación ahora", use_container_width=True):
    with st.spinner("Solicitando permisos y posición..."):
        # Código JavaScript para obtener ubicación con manejo de errores detallado
        js_code = """
        async function getLocation() {
            return new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    reject({ error: true, message: "Geolocalización no soportada por este navegador." });
                    return;
                }
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        resolve({
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            timestamp: position.timestamp
                        });
                    },
                    (err) => {
                        let msg = "";
                        switch(err.code) {
                            case err.PERMISSION_DENIED: msg = "Permiso denegado. Habilita la ubicación en tu navegador."; break;
                            case err.POSITION_UNAVAILABLE: msg = "Información de ubicación no disponible."; break;
                            case err.TIMEOUT: msg = "Tiempo de espera agotado. Intenta de nuevo."; break;
                            default: msg = err.message;
                        }
                        reject({ error: true, message: msg, code: err.code });
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            });
        }
        return await getLocation();
        """
        try:
            result = st_javascript(js_code)
            if result and isinstance(result, dict) and "lat" in result:
                st.session_state.location = result
                st.success(f"✅ Ubicación obtenida: {result['lat']:.5f}, {result['lng']:.5f} (precisión ±{result['accuracy']:.1f} m)")
            elif result and result.get("error"):
                st.error(f"❌ Error de geolocalización: {result.get('message', 'Desconocido')} (Código {result.get('code', '?')})")
                st.info("💡 Consejos: Asegúrate de que la página se esté sirviendo con HTTPS (Streamlit Cloud ya lo hace). Revisa que los permisos de ubicación estén activados en tu navegador.")
            else:
                st.error("No se recibió respuesta del servicio de geolocalización. Intenta recargar la página y volver a dar permisos.")
        except Exception as e:
            st.error(f"Error en la comunicación con el navegador: {e}")

# Mostrar mapa si hay ubicación almacenada
if st.session_state.location:
    loc = st.session_state.location
    lat = loc["lat"]
    lng = loc["lng"]
    accuracy = loc.get("accuracy", 50)

    st.subheader("🗺️ Mapa interactivo")
    
    # Crear mapa centrado en la posición
    m = folium.Map(location=[lat, lng], zoom_start=16, control_scale=True)
    folium.Marker(
        [lat, lng],
        popup=f"📍 Tú estás aquí\nPrecisión: ±{accuracy:.1f} m",
        tooltip="Mi ubicación",
        icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
    ).add_to(m)
    
    # Círculo de precisión
    folium.Circle(
        radius=accuracy,
        location=[lat, lng],
        color="blue",
        fill=True,
        fill_opacity=0.2,
        popup=f"Margen de error ±{accuracy:.1f} m"
    ).add_to(m)
    
    # Mostrar el mapa
    st_folium(m, width=700, height=500, returned_objects=[])
    
    # Mostrar detalles en un expandible
    with st.expander("📋 Datos técnicos"):
        st.write(f"**Latitud:** {lat}")
        st.write(f"**Longitud:** {lng}")
        st.write(f"**Precisión horizontal:** {accuracy:.1f} metros")
        st.write(f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(loc['timestamp']/1000))}")
        st.write(f"**Número ingresado (demo):** {phone}")
else:
    st.info("Presiona el botón **'Obtener mi ubicación ahora'** y permite el acceso a tu ubicación cuando el navegador lo solicite.")

# Pie de página educativo
st.markdown("---")
st.caption("App 100% educativa | Código fuente disponible en GitHub | No se almacena ningún dato personal.")
