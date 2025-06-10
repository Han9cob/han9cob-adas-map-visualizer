import folium

def get_color_for_adas(adas_list):
    adas_set = set([a.upper() for a in adas_list])
    if "CAS" in adas_set:
        return "red"
    if "ACC" in adas_set and "LKA" in adas_set:
        return "green"
    if "ACC" in adas_set and "LDW" in adas_set:
        return "green"
    if "LDW" in adas_set and "TSR" in adas_set:
        return "green"
    if "TSR" in adas_set and len(adas_set) == 1:
        return "orange"
    if "ELKA" in adas_set or "ELKa" in adas_set or "ELKS" in adas_set:
        return "yellow"
    if "TJA" in adas_set:
        return "orange"
    return None  # None means no ADAS, so keep blue

def add_adas_markers_to_map(route_geometry, adas_segments, output_map_path):
    """
    Adds the route and markers for the start and end coordinates of each ADAS segment to a new map.
    - route_geometry: list of [lon, lat] pairs (from OSRM or GeoJSON)
    - adas_segments: list of dicts with 'start', 'end', and 'ADAS' keys
    - output_map_path: path to save the updated map
    """
    # Center the map on the first route point
    if route_geometry:
        first_lat, first_lon = route_geometry[0][1], route_geometry[0][0]
        m = folium.Map(location=[first_lat, first_lon], zoom_start=13)
        # Add the route as a PolyLine
        folium.PolyLine(
            locations=[[lat, lon] for lon, lat in route_geometry],
            color="blue",
            weight=5,
            opacity=0.8
        ).add_to(m)
    else:
        m = folium.Map(location=[0, 0], zoom_start=2)

    # Add ADAS markers
    for seg in adas_segments:
        start_lat, start_lon = seg["start"]
        end_lat, end_lon = seg["end"]
        adas_label = ", ".join(seg["ADAS"]) if isinstance(seg["ADAS"], list) else str(seg["ADAS"])
        folium.Marker(
            location=[start_lat, start_lon],
            popup=f"ADAS Start: {adas_label}",
            icon=folium.Icon(color="blue", icon="play", prefix="fa")
        ).add_to(m)
        folium.Marker(
            location=[end_lat, end_lon],
            popup=f"ADAS End: {adas_label}",
            icon=folium.Icon(color="red", icon="stop", prefix="fa")
        ).add_to(m)

    m.save(output_map_path)
    print(f"ADAS markers added and map saved to: {output_map_path}")

def add_adas_colored_route(route_geometry, adas_segments, output_map_path):
    """
    Colors the route between start and end coordinates of each ADAS segment according to the ADAS features.
    The route is blue by default, and only colored differently where ADAS is active.
    Always marks the start and end of the route.
    """
    if not route_geometry:
        m = folium.Map(location=[0, 0], zoom_start=2)
        m.save(output_map_path)
        return

    first_lat, first_lon = route_geometry[0][1], route_geometry[0][0]
    m = folium.Map(location=[first_lat, first_lon], zoom_start=13)

    # Mark start and end of the route
    folium.Marker(
        location=[route_geometry[0][1], route_geometry[0][0]],
        popup="Route Start",
        icon=folium.Icon(color="green", icon="play", prefix="fa")
    ).add_to(m)
    folium.Marker(
        location=[route_geometry[-1][1], route_geometry[-1][0]],
        popup="Route End",
        icon=folium.Icon(color="red", icon="stop", prefix="fa")
    ).add_to(m)

    # Fit map to start and end points
    m.fit_bounds([
        [route_geometry[0][1], route_geometry[0][0]],
        [route_geometry[-1][1], route_geometry[-1][0]]
    ])

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
            # Add blue segment before this ADAS segment if needed
            if last_idx < start_idx:
                colored_segments.append((route_geometry[last_idx:start_idx+1], "blue"))
            # Add the ADAS-colored segment
            colored_segments.append((route_geometry[start_idx:end_idx+1], color))
            last_idx = end_idx + 1

    # Add remaining blue segment if any
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

    m.save(output_map_path)
    print(f"ADAS-colored route map saved to: {output_map_path}")