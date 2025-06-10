class ADASFeatures:
    def __init__(self, autonomous_level):
        """
        Initialize the ADASFeatures class with the autonomous level.
        """
        self.autonomous_level = autonomous_level
        self.adas_features = self.get_adas_features()

    def get_adas_features(self):
        """
        Map the autonomous level to the corresponding ADAS features.
        """
        adas_features_map = {
            "Level 0 ": ["LDW", "TSR"],
            "Level 1 ": ["LDW", "TSR", "ACC", "ELKA"],
            "Level 2 ": ["TSR", "LKA", "ACC", "ALC", "TJA", "CAS", "PA"],
        }
        return adas_features_map.get(self.autonomous_level, [])

    def save_features(self):
        """
        Save the ADAS features to a variable for future use.
        """
        return self.adas_features