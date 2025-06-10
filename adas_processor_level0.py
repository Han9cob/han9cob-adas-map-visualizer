import csv

class ADASProcessorLevel0:
    def __init__(self, combined_segments):
        self.combined_segments = combined_segments

    def process_adas(self):
        """
        For each combined segment:
        - LDW & TSR if distance > 10 km and duration > 5 min
        - TSR if distance > 2 km
        - None otherwise
        Returns a list of dicts with start, end, ADAS list, distance_km, and duration_min.
        """
        adas_segments = []
        for segment in self.combined_segments:
            start, end = segment[0], segment[1]
            distance_km = segment[3]
            duration_min = segment[4]
            if distance_km > 10 and duration_min > 5:
                adas_list = ["LDW", "TSR"]
            elif distance_km > 2:
                adas_list = ["TSR"]
            else:
                adas_list = ["None"]
            adas_segments.append({
                "start": start,
                "end": end,
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
            writer.writerow(["Start Coordinates", "End Coordinates", "ADAS", "Distance (km)", "Duration (min)"])
            for seg in adas_segments:
                writer.writerow([
                    seg["start"],
                    seg["end"],
                    ", ".join(seg["ADAS"]),
                    seg["distance_km"],
                    seg["duration_min"]
                ])
        print(f"ADAS segments saved to: {output_csv}")