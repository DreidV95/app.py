import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
import requests
import time

st.set_page_config(page_title="Geotracker en Tiempo Real", layout="wide")
st.title("📍 Rastreador de Ubicación GPS en Vivo")
st.markdown("""
**📖 Educativo** – Esta app obtiene la ubicación real de tu dispositivo (móvil/PC) usando el API de Geolocalización del navegador.  
**🔒 Privacidad** – Los datos solo se muestran a ti; no se almacenan ni transmiten externamente (excepto geocodificación inversa pública para mostrar dirección).
""")

# Número de teléfono (demostrativo)
phone = st.text_input("📞 Número de WhatsApp o móvil", value="+573052632705")

# Inicializar session_state
if "last_location" not in st.session_state:
    st.session_state.last_location = None

# Botón para iniciar/actualizar ubicación
if st.button("📍 Obtener mi ubicación ahora", use_container_width=True):
    with st.spinner("Solicitando permisos y posición..."):
        # Usamos st_javascript para obtener coordenadas
        js_code = """
        async function getLocation() {
            return new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    reject("Geolocalización no soportada");
                } else {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            resolve({
                                lat: pos.coords.latitude,
                                lng: pos.coords.longitude,
                                accuracy: pos.coords.accuracy,
                                timestamp: pos.timestamp
                            });
                        },
                        (err) => {
                            reject(err.message);
                        },
                        { enableHighAccuracy: true, timeout: 10000 }
                    );
                }
            });
        }
        return await getLocation();
        """
        location = st_javascript(js_code)
        if location and isinstance(location, dict) and "lat" in location:
            st.session_state.last_location = location
            st.success(f"📍 Posición obtenida: {location['lat']:.5f}, {location['lng']:.5f} (precisión ±{location['accuracy']:.1f} m)")
        else:
            st.error(f"No se pudo obtener ubicación. Error: {location}")

# Función para obtener dirección desde coordenadas (reverse geocoding)
@st.cache_data(ttl=300)
def reverse_geocode(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=18&addressdetails=1"
        headers = {"User-Agent": "StreamlitEducationalApp/1.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("display_name", "Dirección no disponible")
        else:
            return "Servicio de geocodificación no disponible"
    except Exception as e:
        return f"Error: {e}"

# Mostrar mapa si tenemos ubicación
if st.session_state.last_location:
    loc = st.session_state.last_location
    lat, lng = loc["lat"], loc["lng"]
    accuracy = loc.get("accuracy", "?")

    # Dirección aproximada
    address = reverse_geocode(lat, lng)

    st.subheader("🗺️ Mapa interactivo")
    # Crear mapa centrado en la ubicación
    m = folium.Map(location=[lat, lng], zoom_start=16, control_scale=True)
    folium.Marker(
        [lat, lng],
        popup=f"📱 Tu ubicación\nPrecisión: ±{accuracy:.1f}m\n{address}",
        tooltip="Estás aquí",
        icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
    ).add_to(m)
    # Dibujar círculo de precisión
    folium.Circle(
        radius=accuracy,
        location=[lat, lng],
        color="blue",
        fill=True,
        fill_opacity=0.2,
        popup=f"Margen de error ±{accuracy:.1f}m"
    ).add_to(m)

    st_folium(m, width=700, height=500)

    # Mostrar información detallada
    with st.expander("📋 Datos técnicos de la ubicación"):
        st.write(f"**Latitud:** {lat}")
        st.write(f"**Longitud:** {lng}")
        st.write(f"**Precisión horizontal:** {accuracy:.1f} metros")
        st.write(f"**Timestamp:** {time.ctime(loc['timestamp']/1000)}")
        st.write(f"**Dirección aproximada:** {address}")
        st.write(f"**Número ingresado:** {phone}")

    # Explicación educativa
    st.info("""
    **¿Cómo funciona?**
    1. Al hacer clic en el botón, tu navegador solicita permiso para acceder a la ubicación.
    2. El GPS de tu dispositivo (o red WiFi/telefonía) entrega coordenadas.
    3. Streamlit recibe esos datos y los muestra en el mapa usando Folium.
    4. Se hace una consulta a OpenStreetMap para obtener la dirección de forma gratuita.

    **Nota:** Para "tiempo real" continuo, podrías combinar con `st.empty()` y un bucle, pero el estándar de Streamlit recomienda actualizaciones manuales o con `st_autorefresh`.
    """)

else:
    st.info("Haz clic en **'Obtener mi ubicación ahora'** y permite el acceso a tu ubicación cuando el navegador lo solicite.")

# Pie de página educativo
st.markdown("---")
st.caption("App 100% educativa | Código fuente disponible en GitHub | No se almacena ningún dato personal")