import csv

class ADASProcessorLevel1:
    def __init__(self, grouped_highways, grouped_major_roads):
        self.grouped_highways = grouped_highways
        self.grouped_major_roads = grouped_major_roads

    def process_adas(self):
        """
        For each highway segment:
            - ACC + LDW if distance > 5 km
            - ELKA if 2 km < distance <= 5 km
        For each major road segment:
            - TSR if distance > 2 km
        Otherwise: None
        Returns a list of dicts with start, end, ADAS list, distance_km, duration_min, and road_type.
        """
        adas_segments = []

        # Process highways
        for segment in self.grouped_highways:
            start, end = segment[0], segment[1]
            road_type = segment[2]
            distance_km = segment[3]
            duration_min = segment[4]
            if distance_km > 5:
                adas_list = ["ACC", "LDW"]
            elif 1 < distance_km <= 5:
                adas_list = ["ELKA"]
            else:
                adas_list = ["None"]
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
            if distance_km > 2:
                adas_list = ["TSR"]
            else:
                adas_list = ["None"]
            adas_segments.append({
                "start": start,
                "end": end,
                "road_type": road_type,
                "ADAS": adas_list,
                "distance_km": distance_km,
                "duration_min": duration_min
            })

        return adas_segments

    def save_adas_to_csv(self, adas_segments, output_csv):
        """
        Save the ADAS segments to a CSV file.
        """
        with open(output_csv, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Start Coordinates", "End Coordinates", "Road Type", "ADAS", "Distance (km)", "Duration (min)"])
            for seg in adas_segments:
                writer.writerow([
                    seg["start"],
                    seg["end"],
                    seg["road_type"],
                    ", ".join(seg["ADAS"]),
                    seg["distance_km"],
                    seg["duration_min"]
                ])
        print(f"ADAS Level 1 segments saved to: {output_csv}")