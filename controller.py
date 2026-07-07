import config

class Controller:
    def __init__(self, target_dist=config.TARGET_DISTANCE_CM, tolerance=config.TOLERANCE_CM):
        self.target_dist = target_dist
        self.tolerance = tolerance

    @staticmethod
    def get_distance(voltage):
        """
        Linearizes Sharp IR Sensor Voltage and applies piecewise linear interpolation 
        based on new manual calibration data.
        """
        # Step 1: Get the 'raw' captured distance using the baseline power-law formula
        if voltage < 0.1: 
            raw_dist = 100.0
        else:
            try:
                raw_dist = 29.988 * (voltage ** -1.173)
            except (ValueError, ZeroDivisionError):
                raw_dist = 100.0
        
        # Step 2: New Calibration Map (Raw Code Value, Actual Physical Distance)
        cal_map = [
            (15.16, 5.0),
            (27.15, 10.0),
            (39.96, 15.0),
            (45.15, 20.0),
            (66.48, 25.0),
            (69.67, 30.0),
            (77.40, 35.0),
            (90.61, 40.0)
        ]
        
        # Step 3: Interpolate
        if raw_dist <= cal_map[0][0]:
            return cal_map[0][1]
            
        for i in range(len(cal_map) - 1):
            c1, a1 = cal_map[i]
            c2, a2 = cal_map[i+1]
            if c1 <= raw_dist <= c2:
                # Linear Interpolation
                return a1 + (raw_dist - c1) * (a2 - a1) / (c2 - c1)
        
        return cal_map[-1][1]

    def calculate_displacement(self, start_v, end_v):
        """Calculates distance and direction from start and end voltages."""
        d_start = self.get_distance(start_v)
        d_end = self.get_distance(end_v)
        
        displacement = d_end - d_start # Positive means moving AWAY from sensor
        distance = abs(displacement)
        
        # Mapping: Object AWAY -> Lead Screw FORWARD (Away from motor)
        # Mapping: Object TOWARDS -> Lead Screw BACKWARD (Towards motor)
        direction = "FORWARD" if displacement > 0 else "BACKWARD"
        
        return distance, direction

    def get_travel_time(self, distance):
        """Calculates seconds needed to move a distance based on calibrated speed."""
        if config.LEAD_SCREW_SPEED_CMS <= 0:
            return 0.0
        return distance / config.LEAD_SCREW_SPEED_CMS
