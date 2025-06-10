import streamlit as st
from main import process_route  # Import the main route processing function
from streamlit_folium import st_folium
from adas_features import ADASFeatures  # Import the new ADASFeatures class
import time
from add_adas_markers import get_color_for_adas  # Import the helper function for ADAS colors

# --- ADAS Message Function ---
def get_adas_message(vehicle_idx, route_geometry, adas_segments):
    for seg in adas_segments:
        # Find closest indices for start and end
        def find_closest_index(coord):
            lat, lon = coord
            return min(
                range(len(route_geometry)),
                key=lambda i: (route_geometry[i][1] - lat) ** 2 + (route_geometry[i][0] - lon) ** 2
            )
        start_idx = find_closest_index(seg["start"])
        end_idx = find_closest_index(seg["end"])
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        adas_str = ", ".join(seg["ADAS"]) if isinstance(seg["ADAS"], list) else str(seg["ADAS"])

        # Show Disable message from 10 points before end to 10 points after end
        if max(end_idx - 10, 0) <= vehicle_idx <= min(end_idx + 10, len(route_geometry) - 1) and adas_str.lower() != "none":
            return f"""
                <div style='text-align: right; color: orange; font-weight: bold; font-size: 18px;'>
                    Disable: {adas_str}
                </div>
            """
        # Show Enable message from 5 points before start until 10 points before end
        if max(start_idx - 5, 0) <= vehicle_idx < max(end_idx - 10, 0) and adas_str.lower() != "none":
            return f"""
                <div style='text-align: right; color: green; font-weight: bold; font-size: 18px;'>
                    Enable: {adas_str}
                </div>
            """
    return None

# --- Page Configuration ---
st.set_page_config(
    page_title="Route Processor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    .header {
        color: #007bff;
        text-align: center;
        padding-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown("<h1 class='header'>In-Vehicle Navigation System</h1>", unsafe_allow_html=True)

# --- Input Fields ---
st.sidebar.header("Enter the location within Germany")
source = st.sidebar.text_input("Source Location", "Heilbronn")
destination = st.sidebar.text_input("Destination Location", "Neckarsulm")
autonomous_level = st.sidebar.selectbox(
    "Autonomous Level",
    ["Level 0 ", "Level 1 ", "Level 2 "],
    index=0
)

# --- Session State Initialization ---
if "simulating" not in st.session_state:
    st.session_state.simulating = False
if "vehicle_idx" not in st.session_state:
    st.session_state.vehicle_idx = 0
if "just_incremented" not in st.session_state:
    st.session_state.just_incremented = False

# --- Calculate Route Button ---
if st.sidebar.button("Calculate Route"):
    if not source or not destination:
        st.error("Please enter both source and destination.")
    else:
        try:
            # Display the "Processing route..." message on the UI
            st.write(f"Processing route from {source} to {destination} with Autonomous Level: {autonomous_level}...")

            # Call the main route processing function
            route_details = process_route(source, destination, autonomous_level.strip())

            # Save the results in session state
            st.session_state["route_details"] = route_details
            st.session_state["route_map"] = route_details.get("route_map")
            st.session_state.vehicle_idx = 0
            st.session_state.simulating = False

        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- Simulation Controls ---
# Only show simulation controls if a route is available
if "route_details" in st.session_state and st.session_state["route_details"].get("route_geometry"):
    st.sidebar.markdown("---")
    st.sidebar.header("Simulation Controls")
    speed_kmph = st.sidebar.slider("Vehicle Speed (kmph)", 10, 100, value=10, step=10)
    st.sidebar.write(f"Selected Speed: {speed_kmph} kmph")
    speed = speed_kmph // 10  # 1 point = 10 kmph

    if st.sidebar.button("Start Simulation"):
        st.session_state.simulating = True

    if st.sidebar.button("Stop Simulation"):
        st.session_state.simulating = False

    if st.sidebar.button("Reset Simulation"):
        st.session_state.vehicle_idx = 0
        st.session_state.simulating = False
else:
    speed = 1  # Default value if no route yet

# Move the vehicle if simulation is running
if (
    st.session_state.get("simulating", False)
    and "route_details" in st.session_state
    and st.session_state["route_details"].get("route_geometry")
):
    route_geometry = st.session_state["route_details"]["route_geometry"]
    if not st.session_state.just_incremented:
        if st.session_state.vehicle_idx < len(route_geometry) - 1:
            st.session_state.vehicle_idx = min(
                st.session_state.vehicle_idx + speed, len(route_geometry) - 1
            )
            st.session_state.just_incremented = True
            time.sleep(0.2)  # Animation delay
            st.rerun()
        else:
            st.session_state.simulating = False  # Stop at the end
    else:
        st.session_state.just_incremented = False

# --- Layout: Two Columns ---
col1, col2 = st.columns([3, 1])  # Left (Map) and Right (Route Info + ADAS Features)

# --- Left Pane: Map ---
with col1:
    st.subheader("Route Map")
    if "route_details" in st.session_state and st.session_state["route_details"].get("route_geometry"):
        route_geometry = st.session_state["route_details"]["route_geometry"]
        adas_segments = st.session_state["route_details"].get("adas_segments", [])
        if st.session_state.get("simulating", False):
            # --- Dynamic ADAS Message ---
            message_html = get_adas_message(
                st.session_state.vehicle_idx,
                route_geometry,
                adas_segments
            )
            if message_html:
                st.markdown(message_html, unsafe_allow_html=True)
            # Show dynamic map with moving vehicle marker
            import folium
            from streamlit_folium import st_folium

            idx = st.session_state.vehicle_idx
            vehicle_lat, vehicle_lon = route_geometry[idx][1], route_geometry[idx][0]
            # Center the map on the current vehicle position
            m = folium.Map(location=[vehicle_lat, vehicle_lon], zoom_start=13)

            # Helper to find the closest index in route_geometry for a given (lat, lon)
            def find_closest_index(coord):
                lat, lon = coord
                return min(
                    range(len(route_geometry)),
                    key=lambda i: (route_geometry[i][1] - lat) ** 2 + (route_geometry[i][0] - lon) ** 2
                )

            # Build a list of colored segments
            colored_segments = []
            last_idx = 0
            for seg in adas_segments:
                start_idx = find_closest_index(seg["start"])
                end_idx = find_closest_index(seg["end"])
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                color = get_color_for_adas(seg["ADAS"])
                if color:  # Only color if ADAS is active
                    if last_idx < start_idx:
                        colored_segments.append((route_geometry[last_idx:start_idx+1], "blue"))
                    colored_segments.append((route_geometry[start_idx:end_idx+1], color))
                    last_idx = end_idx + 1

            if last_idx < len(route_geometry):
                colored_segments.append((route_geometry[last_idx:], "blue"))

            # Draw all segments
            for coords, color in colored_segments:
                folium.PolyLine(
                    locations=[[lat, lon] for lon, lat in coords],
                    color=color,
                    weight=7,
                    opacity=0.9
                ).add_to(m)

            folium.Marker(
                location=[vehicle_lat, vehicle_lon],
                popup="Vehicle",
                icon=folium.Icon(color="red", icon="car", prefix="fa")
            ).add_to(m)

            st_folium(m, width=700, height=500)
        else:
            # Show the static HTML map from main.py
            try:
                with open("route_map_with_adas.html", "r", encoding="utf-8") as f:
                    map_html = f.read()
                st.components.v1.html(map_html, height=500, width=700)
            except Exception:
                st.info("Map file not found. Please calculate a route.")
    else:
        st.info("No route to display. Please calculate a route first.")

# --- Right Pane: Route Information and ADAS Features ---
with col2:
    if "route_details" in st.session_state:
        st.subheader("Route Details")
        route_details = st.session_state["route_details"]

        # Display all route details returned from main.py
        for key, value in route_details.items():
            if key in ["adas_segments", "route_geometry"]:
                continue  # Skip printing adas_segments and route_geometry here
            pretty_key = key.replace("_", " ").capitalize()
            if isinstance(value, float):
                st.write(f"**{pretty_key}:** {value:.2f}")
            else:
                st.write(f"**{pretty_key}:** {value}")

    # --- ADAS Segments Table ---
    if "route_details" in st.session_state and "adas_segments" in st.session_state["route_details"]:
        st.markdown("---")
        st.subheader("ADAS Details")
        adas_segments = st.session_state["route_details"]["adas_segments"]
        for idx, seg in enumerate(adas_segments, 1):
            adas_str = ", ".join(seg["ADAS"]) if isinstance(seg["ADAS"], list) else str(seg["ADAS"])
            if adas_str.strip().lower() == "none":
                continue  # Skip segments with no ADAS
            distance = seg.get("distance_km", "N/A")
            duration = seg.get("duration_min", "N/A")
            color = seg.get("color", "blue")
            st.markdown(
                f"""
                <div style='margin-bottom:10px;'>
                    <b>Segment {idx}:</b><br>
                    <b>ADAS:</b> {adas_str}<br>
                    <b>Distance:</b> {distance} km<br>
                    <b>Duration:</b> {duration} min<br>
                    <b>Color:</b> <span style='color:{color};font-weight:bold'>{color}</span>
                </div>
                """,
                unsafe_allow_html=True
            )


