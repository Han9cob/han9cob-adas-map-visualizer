import json
from routeprocessing import RouteProcessor
from identify_highways import HighwayIdentifier
from identify_major_roads import MajorRoadIdentifier
from identify_local_roads import LocalRoadIdentifier
from combined_road_grouper import CombinedRoadGrouper
from adas_processor_level0 import ADASProcessorLevel0 
from adas_processor_level1 import ADASProcessorLevel1
from adas_processor_level2 import ADASProcessorLevel2
from add_adas_markers import add_adas_markers_to_map, add_adas_colored_route, get_color_for_adas
import streamlit as st

def process_route(source, destination, autonomous_level):
    """
    Process the route and return the distance, duration, intersection data, and ADAS segments.
    """
    processor = RouteProcessor()
    source_coords = processor.get_lat_lon(source)
    destination_coords = processor.get_lat_lon(destination)

    distance, duration, intersection_data, route_geometry = processor.calculate_shortest_route(
        source_coords,
        destination_coords,
        output_file="shortest_path_output.json",
        map_file="route_map.html"
    )

    highway_identifier = HighwayIdentifier(intersection_data)
    grouped_highways = highway_identifier.group_highways()
    highway_identifier.save_grouped_to_csv(grouped_highways, "grouped_highways.csv")

    major_road_identifier = MajorRoadIdentifier(intersection_data)
    grouped_major_roads = major_road_identifier.group_major_roads()
    major_road_identifier.save_grouped_to_csv(grouped_major_roads, "grouped_major_roads.csv")

    local_road_identifier = LocalRoadIdentifier(intersection_data)
    grouped_local_roads = local_road_identifier.group_local_roads()
    local_road_identifier.save_grouped_to_csv(grouped_local_roads, "grouped_local_roads.csv")

    grouper = CombinedRoadGrouper(grouped_highways, grouped_major_roads)
    combined_segments = grouper.combine()
    grouper.save_combined_to_csv(combined_segments, "combined_highway_major_road.csv")

    # ADAS processing based on autonomous level
    adas_segments = []
    if autonomous_level == "Level 0":
        adas_processor = ADASProcessorLevel0(combined_segments)
        adas_segments = adas_processor.process_adas()
        adas_processor.save_adas_to_csv(adas_segments, "adas_segments_level0.csv")
    elif autonomous_level == "Level 1":
        adas_processor = ADASProcessorLevel1(grouped_highways, grouped_major_roads)
        adas_segments = adas_processor.process_adas()
        adas_processor.save_adas_to_csv(adas_segments, "adas_segments_level1.csv")
    elif autonomous_level == "Level 2":
        adas_processor = ADASProcessorLevel2(grouped_highways, grouped_major_roads, grouped_local_roads)
        adas_segments = adas_processor.process_adas()
        adas_processor.save_adas_to_csv(adas_segments, "adas_segments_level2.csv")

    add_adas_colored_route(route_geometry, adas_segments, "route_map_with_adas.html")

    # Add color info to each ADAS segment
    for seg in adas_segments:
        seg["color"] = get_color_for_adas(seg["ADAS"])

    return {
        "route_distance_km": distance / 1000,
        "estimated_duration_minutes": duration / 60,
        "adas_segments": adas_segments,
        "route_geometry": route_geometry  # <-- This must be present and not empty!
    }

# Streamlit UI
if __name__ == "__main__":
    st.title("Route Visualization")

    source = "Heilbronn"
    destination = "NeckarSulm"
    autonomous_level = st.sidebar.selectbox(
        "Autonomous Level",
        ["Level 0", "Level 1", "Level 2"],
        index=0
    )

    route_details = process_route(source, destination, autonomous_level)

    with open("route_map_with_adas.html", "r", encoding="utf-8") as f:
        map_html = f.read()
    st.components.v1.html(map_html, height=500, width=700)

    st.write("Route Details:", route_details)

