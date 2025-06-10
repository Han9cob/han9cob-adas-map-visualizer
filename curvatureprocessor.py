import math

class CurvatureProcessor:
    def __init__(self, route_coords):
        """
        Initialize the CurvatureProcessor with route coordinates.
        :param route_coords: List of route coordinates [(lat1, lon1), (lat2, lon1), ...].
        """
        self.route_coords = route_coords
        self.curvatures = []  # List to store curvature data

    def calculate_angle(self, p1, p2, p3):
        """
        Calculate the signed angle (in degrees) between three points.
        Positive angle indicates a right turn (clockwise),
        Negative angle indicates a left turn (counterclockwise).
        :param p1: First point (lat, lon).
        :param p2: Middle point (lat, lon).
        :param p3: Third point (lat, lon).
        :return: Signed angle in degrees.
        """
        # Convert points to radians
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        lat3, lon3 = math.radians(p3[0]), math.radians(p3[1])

        # Calculate vectors
        vector1 = (lat2 - lat1, lon2 - lon1)
        vector2 = (lat3 - lat2, lon3 - lon2)

        # Calculate dot product and magnitudes
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        magnitude1 = math.sqrt(vector1[0]**2 + vector1[1]**2)
        magnitude2 = math.sqrt(vector2[0]**2 + vector2[1]**2)

        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0

        # Calculate the angle in radians
        angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))

        # Calculate the cross product to determine the sign of the angle
        cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]

        # Convert the angle to degrees and apply the sign
        angle_degrees = math.degrees(angle_radians)
        if cross_product < 0:
            angle_degrees = -angle_degrees  # Negative for left turns

        return angle_degrees

    def calculate_distance(self, coord1, coord2):
        """
        Calculate the distance between two coordinates (latitude, longitude) using the Haversine formula.
        :param coord1: Tuple of (latitude, longitude) for the first point.
        :param coord2: Tuple of (latitude, longitude) for the second point.
        :return: Distance in kilometers.
        """
        R = 6371  # Radius of the Earth in kilometers
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c  # Distance in kilometers

    def process_curvatures(self):
        """
        Process the route to calculate complete curvatures.
        A new curve starts whenever there is a sign change in the angle.
        :return: List of curvatures with start point, end point, total angle, and total distance.
        """
        in_curvature = False
        start_point = None
        total_angle = 0
        total_distance = 0
        previous_sign = None  # Track the sign of the previous angle

        for i in range(1, len(self.route_coords) - 1):
            p1 = self.route_coords[i - 1]
            p2 = self.route_coords[i]
            p3 = self.route_coords[i + 1]

            # Calculate curvature angle
            angle = self.calculate_angle(p1, p2, p3)
            current_sign = 1 if angle > 0 else -1 if angle < 0 else 0

            # Check for sign change or angle deviation from zero
            if current_sign != previous_sign and previous_sign is not None:
                if in_curvature:
                    # Save the current curve before starting a new one
                    self.curvatures.append({
                        "start": start_point,
                        "end": p2,
                        "angle": total_angle,
                        "distance": total_distance
                    })
                    # Reset curvature tracking variables
                    in_curvature = False
                    total_angle = 0
                    total_distance = 0

            if angle != 0:  # Start or continue a curvature
                if not in_curvature:
                    # Start of a new curvature
                    in_curvature = True
                    start_point = p1
                total_angle += abs(angle)  # Use absolute value to accumulate total angle
                total_distance += self.calculate_distance(p1, p2)

            # Update the previous sign
            previous_sign = current_sign

        # Save the last curve if it was in progress
        if in_curvature:
            self.curvatures.append({
                "start": start_point,
                "end": self.route_coords[-1],
                "angle": total_angle,
                "distance": total_distance
            })

        return self.curvatures

    def save_curvatures_to_file(self, file_path="curvatures.txt"):
        """
        Save the curvature data to a file.
        :param file_path: Path to the file where curvature data will be saved.
        """
        with open(file_path, "w") as file:
            for curve in self.curvatures:
                file.write(f"Start: {curve['start']}, End: {curve['end']}, "
                           f"Total Angle: {curve['angle']:.2f} degrees, "
                           f"Total Distance: {curve['distance']:.2f} km\n")
