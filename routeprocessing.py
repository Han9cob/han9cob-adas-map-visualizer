import requests
import folium
import webbrowser
from geopy.geocoders import Nominatim
import tempfile
import os
import csv
import osmnx as ox

class RouteProcessor:
    def __init__(self, osrm_base_url="http://localhost:5000"):
        """
        Initialize the RouteProcessor with the base URL of the OSRM server and the geopy Nominatim geolocator.
        """
        self.osrm_base_url = osrm_base_url
        self.geolocator = Nominatim(user_agent="route_processor")

    def get_lat_lon(self, location):
        """
        Convert a location (e.g., city name) into latitude and longitude using geopy's Nominatim geocoder.
        """
        try:
            location_data = self.geolocator.geocode(location)
            if location_data:
                return location_data.latitude, location_data.longitude
            else:
                raise ValueError(f"Could not find latitude and longitude for location: {location}")
        except Exception as e:
            raise ValueError(f"Error while fetching latitude and longitude: {e}")

    def calculate_shortest_route(self, source_coords, destination_coords, output_file="route_output.json", map_file="route_map.html", csv_file="intersections.csv"):
        """
        Call the OSRM server to calculate the shortest route between source and destination.
        Save and print the route details, save the route to a map, and save intersection data to a CSV file.
        :param source_coords: Tuple of (latitude, longitude) for the source.
        :param destination_coords: Tuple of (latitude, longitude) for the destination.
        :param output_file: File to save the route details.
        :param map_file: File to save the route map.
        :param csv_file: File to save the intersection data.
        :return: distance, duration, intersection_data, route_geometry
        """
        try:
            # Construct the OSRM API URL
            url = f"{self.osrm_base_url}/route/v1/driving/{source_coords[1]},{source_coords[0]};{destination_coords[1]},{destination_coords[0]}"
        
            # Send the request to the OSRM server
            response = requests.get(url, params={
                "overview": "full",       # Include the full geometry of the route
                "geometries": "geojson",  # Use GeoJSON format for the route geometry
                "steps": "true"           # Include step-by-step instructions
            })
            response.raise_for_status()  # Raise an error for HTTP issues

            # Parse the JSON response
            data = response.json()

            # Check if the OSRM response is valid
            if data["code"] == "Ok":
                # Save the route details to a file
                with open(output_file, "w") as file:
                    import json
                    json.dump(data, file, indent=4)

                # Print the route details
                print("Route details saved to:", output_file)
                #print("Route geometry (coordinates):", data["routes"][0]["geometry"]["coordinates"])
                print("Total distance (meters):", data["routes"][0]["distance"])
                print("Total duration (seconds):", data["routes"][0]["duration"])

                # Extract the route geometry
                route_geometry = data["routes"][0]["geometry"]["coordinates"]

                # Create a map centered on the source coordinates
                route_map = folium.Map(location=[source_coords[0], source_coords[1]], zoom_start=13)

                # Add the route to the map
                folium.PolyLine(
                    locations=[[lat, lon] for lon, lat in route_geometry],  # Reverse coordinates for folium
                    color="blue",
                    weight=5,
                    opacity=0.8
                ).add_to(route_map)

                # Add markers for the source and destination
                folium.Marker(location=[source_coords[0], source_coords[1]], popup="Source", icon=folium.Icon(color="green")).add_to(route_map)
                folium.Marker(location=[destination_coords[0], destination_coords[1]], popup="Destination", icon=folium.Icon(color="red")).add_to(route_map)

                # Save the map to an HTML file
                route_map.save(map_file)
                print("Route map saved to:", map_file)

                # Extract intersection data and save to CSV
                steps = data["routes"][0]["legs"][0]["steps"]
                intersection_data = extract_intersection_data(steps)
                save_to_csv(intersection_data, csv_file)

                # Return distance, duration, intersection_data, and route_geometry
                return data["routes"][0]["distance"], data["routes"][0]["duration"], tuple(intersection_data), route_geometry
            else:
                print(f"OSRM error: {data['code']} - {data.get('message', 'No message provided')}")

        except Exception as e:
            print(f"Error while calculating the shortest route: {e}")
            return None, None, (), []

    def calculate_shortest_path(self, source_coords, destination_coords, output_file="shortest_path_output.json", map_file="route_map.html"):
        """
        Calculate the shortest path between source and destination using OSRM,
        save the route details to a JSON file, and save the route map as HTML.
        """
        try:
            # Construct the OSRM API URL
            url = f"{self.osrm_base_url}/route/v1/driving/{source_coords[1]},{source_coords[0]};{destination_coords[1]},{destination_coords[0]}"
            
            # Send the request to the OSRM server
            response = requests.get(url, params={
                "overview": "full",
                "geometries": "geojson",
                "steps": "true"
            })
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Check if the OSRM response is valid
            if data["code"] == "Ok":
                route = data["routes"][0]
                # Save route details to a file
                with open(output_file, "w") as file:
                    json.dump({
                        "distance": route["distance"],
                        "duration": route["duration"],
                        "geometry": route["geometry"]["coordinates"],
                        "legs": route.get("legs", [])
                    }, file, indent=4)

                # Generate and save the map
                route_geometry = route["geometry"]["coordinates"]
                route_map = folium.Map(location=[source_coords[0], source_coords[1]], zoom_start=13)
                folium.PolyLine(
                    locations=[[lat, lon] for lon, lat in route_geometry],
                    color="blue",
                    weight=5,
                    opacity=0.8
                ).add_to(route_map)
                folium.Marker(location=[source_coords[0], source_coords[1]], popup="Source", icon=folium.Icon(color="green")).add_to(route_map)
                folium.Marker(location=[destination_coords[0], destination_coords[1]], popup="Destination", icon=folium.Icon(color="red")).add_to(route_map)
                route_map.save(map_file)

                return route_geometry, route["distance"], route["duration"], route.get("legs", [])
            else:
                raise ValueError(f"OSRM error: {data['code']} - {data.get('message', 'No message provided')}")
        except Exception as e:
            raise ValueError(f"Error while calculating the shortest path: {e}")

def extract_intersection_data(steps):
    """
    Extract intersection data from the steps information in the OSRM route output.
    :param steps: List of steps from the OSRM route output.
    :return: List of tuples containing intersection data.
    """
    intersection_data = []
    previous_name = None
    previous_ref = None

    for i, step in enumerate(steps):
        coords = step["geometry"]["coordinates"]
        # Swap lon,lat to lat,lon
        start_coords = (coords[0][1], coords[0][0])
        end_coords = (coords[-1][1], coords[-1][0])
        if len(coords) > 2:
            mid_index = len(coords) // 2
            intermediate_coord = (coords[mid_index][1], coords[mid_index][0])
        else:
            intermediate_coord = None

        name = step.get("name", "N/A")
        ref = step.get("ref", "N/A")
        distance = step.get("distance", 0)
        duration = step.get("duration", 0)
        modifier = step.get("maneuver", {}).get("modifier", "N/A")
        maneuver_type = step.get("maneuver", {}).get("type", "N/A")

        # Use the new combined logic for road type, passing end_coords if intermediate_coord is None
        road_type = get_combined_road_type(ref, intermediate_coord if intermediate_coord else end_coords)

        if maneuver_type in ["depart", "arrive"]:
            is_road_change = False
        else:
            next_name = steps[i + 1].get("name", "N/A") if i + 1 < len(steps) else None
            is_road_change = (
                name == "" and
                previous_name is not None and
                next_name is not None and
                previous_name != next_name
            )

        intersection_tuple = (
            start_coords,
            end_coords,
            intermediate_coord,
            name,
            ref,
            distance,
            duration,
            modifier,
            maneuver_type,
            road_type,
            is_road_change
        )

        intersection_data.append(intersection_tuple)
        previous_name = name
        previous_ref = ref

    return intersection_data

def save_to_csv(intersection_data, output_csv):
    """
    Save the intersection data to a CSV file.
    :param intersection_data: List of tuples containing intersection data.
    :param output_csv: Path to the output CSV file.
    """
    with open(output_csv, "w", newline="") as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Start Coordinates", "End Coordinates", "Intermediate Coordinate", "Name", "Ref", "Distance", "Duration", "Modifier", "Type", "Road Type", "Road Change"])
        # Write the data
        writer.writerows(intersection_data)

    print(f"Intersection data saved to: {output_csv}")

def get_combined_road_type(ref, coord):
    """
    Classify the road type based on the reference number or OSMNX.
    :param ref: The reference of the road.
    :param coord: The coordinate (lat, lon) to use for OSMNX lookup.
    :return: The classified road type.
    """
    # If ref is available and starts with "A" or "B", classify as Highway
    if ref and ref != "N/A" and ref != "" and (ref.startswith("A") or ref.startswith("B")):
        return "Highway"
    # Otherwise, use OSMNX with the provided coordinate (intermediate or end)
    if coord:
        lat, lon = coord  # coord is already (lat, lon)
        try:
            G = ox.graph_from_point((lat, lon), dist=50, network_type="all")
            for _, _, data in G.edges(data=True):
                if "highway" in data:
                    highway_type = data["highway"]
                    if isinstance(highway_type, list):
                        highway_type = highway_type[0]
                    # Highway and Highway_link
                    if highway_type in ["motorway", "trunk"]:
                        return "Highway"
                    elif highway_type in ["motorway_link", "trunk_link"]:
                        return "Highway_link"
                    # Major Road and MajorRoad_link
                    elif highway_type in ["primary", "secondary", "tertiary"]:
                        return "Major Road"
                    elif highway_type in ["primary_link", "secondary_link", "tertiary_link"]:
                        return "MajorRoad_link"
                    elif highway_type in ["residential", "unclassified", "living_street"]:
                        return "Local Road"
                    elif highway_type in ["service", "rest_area"]:
                        return "Service Road"
                    else:
                        return "Other"
            return "Unknown"
        except Exception as e:
            # print(f"Error fetching road type from OSMNX for ({lat}, {lon}): {e}")
            return "Error"
    else:
        return "Unknown"



