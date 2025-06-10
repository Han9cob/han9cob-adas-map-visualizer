import csv

class HighwayIdentifier:
    def __init__(self, intersection_data):
        self.intersection_data = intersection_data

    def group_highways(self):
        """
        Groups consecutive intersections where:
        - road_type is 'Highway'
        - maneuver_type is not 'turn'
        - modifier is in ['slight left', 'slight right', 'straight']
        Starts a group only when all conditions are met, ends when any is not met.
        Returns a list of grouped segments: (start_coords, end_coords, road_type, total_distance_km, total_duration_min)
        """
        if not self.intersection_data:
            return []

        grouped = []
        current_group = None

        for entry in self.intersection_data:
            start_coords = entry[0]
            end_coords = entry[1]
            modifier = entry[7]
            maneuver_type = entry[8]
            road_type = entry[9]
            distance = entry[5]
            duration = entry[6]

            # Check if all conditions to be in a group are met
            in_group = (
                road_type in ["Highway"] and
                maneuver_type != "turn" and
                modifier in ["slight left", "slight right", "straight"]
            )

            if in_group:
                if current_group is None:
                    # Start a new group
                    current_group = {
                        "start": start_coords,
                        "end": end_coords,
                        "road_type": road_type,
                        "distance": distance,
                        "duration": duration
                    }
                else:
                    # Extend the current group
                    current_group["end"] = end_coords
                    current_group["distance"] += distance
                    current_group["duration"] += duration
            else:
                if current_group is not None:
                    # End the current group (convert units)
                    grouped.append((
                        current_group["start"],
                        current_group["end"],
                        current_group["road_type"],
                        round(current_group["distance"] / 1000, 3),   # km
                        round(current_group["duration"] / 60, 2)      # min
                    ))
                    current_group = None
                # Do not start a new group until all conditions are met again

        # Add the last group if it exists
        if current_group is not None:
            grouped.append((
                current_group["start"],
                current_group["end"],
                current_group["road_type"],
                round(current_group["distance"] / 1000, 3),   # km
                round(current_group["duration"] / 60, 2)      # min
            ))

        return grouped

    def save_grouped_to_csv(self, grouped_data, output_csv):
        with open(output_csv, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Start Coordinates", "End Coordinates", "Road Type", "Total Distance (km)", "Total Duration (min)"])
            for row in grouped_data:
                writer.writerow(row)
        print(f"Grouped highway data saved to: {output_csv}")