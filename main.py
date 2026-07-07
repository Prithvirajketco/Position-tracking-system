import time
import config
from daq_interface import DAQInterface
from controller import Controller

def main():
    print(f"--- EMS 2 Record & Mimic System ---")
    print(f"Calibrated Speed: {config.LEAD_SCREW_SPEED_CMS} cm/s")
    print(f"Simulation Mode: {config.SIMULATION_MODE}")
    print("-----------------------------------\n")

    with DAQInterface(simulation=config.SIMULATION_MODE) as daq:
        ctrl = Controller()
        
        # 1. Homing Sequence
        daq.home_motor()
        
        # 2. Initial State
        # The user requested to start with an initial reading of 5.0cm
        last_dist = 5.0 
        print(f"\nSystem Initialized at {last_dist:.2f} cm")

        try:
            while True:
                print(f"\nREADY: Move the object to NEW position and press [ENTER].")
                print(f"(Reference position: {last_dist:.2f} cm)")
                input()
                
                v_end = daq.read_sensor_voltage()
                current_dist = ctrl.get_distance(v_end)
                print(f"Captured New Position: {current_dist:.2f} cm")

                # Calculate movement requirements relative to previous position
                displacement = current_dist - last_dist
                dist = abs(displacement)
                direction = "FORWARD" if displacement > 0 else "BACKWARD"
                
                travel_time = ctrl.get_travel_time(dist)

                if dist < 0.1: # Small noise threshold
                    print("No significant movement detected.")
                    continue

                print(f"\nACTION: Mimicking movement of {dist:.2f} cm {direction}...")
                print(f"Estimated Time: {travel_time:.2f} seconds")
                
                # Execution
                start_time = time.time()
                while (time.time() - start_time) < travel_time:
                    # Check Limits for Safety
                    limits = daq.read_limit_switches()
                    if (direction == "BACKWARD" and not limits[0]) or \
                       (direction == "FORWARD" and not limits[1]):
                        print(f"\n[SAFETY STOP] Hit {direction} limit switch!")
                        break
                    
                    # Apply Motor Command
                    if direction == "FORWARD":
                        daq.set_motor(True, False, True)
                    else:
                        daq.set_motor(False, True, True)
                    
                    time.sleep(0.05)
                
                daq.stop_motor()
                
                # Update reference for next iteration
                last_dist = current_dist
                print("\nMovement Complete.")
                print("-" * 30)

        except KeyboardInterrupt:
            print("\nShutting down...")
            daq.stop_motor()

if __name__ == "__main__":
    main()
