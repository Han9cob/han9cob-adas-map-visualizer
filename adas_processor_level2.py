import csv

class ADASProcessorLevel2:
    def __init__(self, grouped_highways, grouped_major_roads, grouped_local_roads):
        self.grouped_highways = grouped_highways
        self.grouped_major_roads = grouped_major_roads
        self.grouped_local_roads = grouped_local_roads

    def process_adas(self):
        """
        For each highway segment:
            - ACC, LKA if distance > 5 km
            - ELKA if 1 < distance <= 5 km
        For each major road:
            - TJA if distance > 1 km
        For each local road segment:
            - CAS if distance > 1 km
        Otherwise: None (do not include in output)
        Returns a list of dicts with start, end, road_type, ADAS list, distance_km, duration_min.
        """
        adas_segments = []

        # Process highways
        for segment in self.grouped_highways:
            start, end = segment[0], segment[1]
            road_type = segment[2]
            distance_km = segment[3]
            duration_min = segment[4]
            if distance_km > 5:
                adas_list = ["ACC", "LKA"]
            elif 1 < distance_km <= 5:
                adas_list = ["ELKA"]
            else:
                continue  # Skip segments with no ADAS
            adas_segments.append({
                "start": start,
                "end": end,
                "road_type": road_type,
                "ADAS": adas_list,
                "distance_km": distance_km,
                "duration_min": duration_min
            })

        # Process major roads
        for segment in self.grouped_major_roads:
            start, end = segment[0], segment[1]
            road_type = segment[2]
            distance_km = segment[3]
            duration_min = segment[4]
            if distance_km > 1:
                adas_list = ["TJA"]
            else:
                continue  # Skip segments with no ADAS
            adas_segments.append({
                "start": start,
                "end": end,
                "road_type": road_type,
                "ADAS": adas_list,
                "distance_km": distance_km,
                "duration_min": duration_min
            })

        # Process local roads
        for segment in self.grouped_local_roads:
            start, end = segment[0], segment[1]
            road_type = segment[2]
            distance_km = segment[3]
            duration_min = segment[4]
            if distance_km > 1:
                adas_list = ["CAS"]
            else:
                continue  # Skip segments with no ADAS
            adas_segments.append({
                "start": start,
                "end": end,
                "road_type": road_type,
                "ADAS": adas_list,
                "distance_km": distance_km,
                "duration_min": duration_min
            })

        return adas_segments

    # def save_adas_to_csv(self, adas_segments, output_csv):
    #     """
    #     Save the ADAS segments to a CSV file.
    #     """
    #     with open(output_csv, "w", newline="") as file:
    #         writer = csv.writer(file)
    #         writer.writerow(["Start Coordinates", "End Coordinates", "Road Type", "ADAS", "Distance (km)", "Duration (min)"])
    #         for seg in adas_segments:
    #             writer.writerow([
    #                 seg["start"],
    #                 seg["end"],
    #                 seg["road_type"],
    #                 ", ".join(seg["ADAS"]),
    #                 seg["distance_km"],
    #                 seg["duration_min"]
    #             ])
    #     # print(f"ADAS Level 2 segments saved to: {output_csv}")