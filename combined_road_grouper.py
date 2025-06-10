class CombinedRoadGrouper:
    def __init__(self, grouped_highways, grouped_major_roads):
        self.grouped_highways = grouped_highways
        self.grouped_major_roads = grouped_major_roads

    def combine(self):
        """
        Combine highway and major road segments if the end of one matches the start of the other.
        Returns a list of combined segments: (start, end, road_types, total_distance_km, total_duration_min)
        """
        combined = []
        used_major = set()

        for h_idx, h in enumerate(self.grouped_highways):
            h_start, h_end, h_type, h_dist, h_dur = h
            merged = False
            for m_idx, m in enumerate(self.grouped_major_roads):
                if m_idx in used_major:
                    continue
                m_start, m_end, m_type, m_dist, m_dur = m
                # If highway end matches major road start, or vice versa
                if h_end == m_start:
                    combined.append((
                        h_start,
                        m_end,
                        f"{h_type}+{m_type}",
                        round(h_dist + m_dist, 3),
                        round(h_dur + m_dur, 2)
                    ))
                    used_major.add(m_idx)
                    merged = True
                    break
                elif m_end == h_start:
                    combined.append((
                        m_start,
                        h_end,
                        f"{m_type}+{h_type}",
                        round(m_dist + h_dist, 3),
                        round(m_dur + h_dur, 2)
                    ))
                    used_major.add(m_idx)
                    merged = True
                    break
            if not merged:
                # If not merged, keep the highway as is
                combined.append(h)

        # Add any major roads that were not merged
        for m_idx, m in enumerate(self.grouped_major_roads):
            if m_idx not in used_major:
                combined.append(m)

        return combined

    def save_combined_to_csv(self, combined_data, output_csv):
        import csv
        with open(output_csv, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Start Coordinates", "End Coordinates", "Road Types", "Total Distance (km)", "Total Duration (min)"])
            for row in combined_data:
                writer.writerow(row)
        print(f"Combined road data saved to: {output_csv}")