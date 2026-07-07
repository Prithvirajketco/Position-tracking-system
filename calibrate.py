import time
import config
from daq_interface import DAQInterface

def calibrate():
    print("--- EMS 2 Forced Calibration ---")
    print("Motor will run forward for EXACTLY 10 seconds.")
    print("WARNING: Limit switches are DISABLED. Ensure the carriage has enough room!")
    
    CALIBRATION_DURATION = 10.0  # seconds
    
    with DAQInterface(simulation=config.SIMULATION_MODE) as daq:
        print(f"\nMotor started. Moving forward for {CALIBRATION_DURATION} seconds...")
        start_time = time.time()
        
        try:
            while True:
                actual_elapsed = time.time() - start_time
                
                # Check for 10-second timeout
                if actual_elapsed >= CALIBRATION_DURATION:
                    break
                
                # Drive Forward (Away from motor)
                # set_motor(in1, in2, pwm)
                daq.set_motor(True, False, True) 
                time.sleep(0.1) # Frequency doesn't matter as much now
                
        finally:
            # This ensures the motor stops even if you Ctrl+C or at the end of 10s
            daq.stop_motor()
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n--- Results ---")
            print(f"Total Run Time: {total_time:.2f} seconds")
            print("----------------")
            print("1. Measure the physical distance moved (cm).")
            print("2. Count the number of revolutions made by the lead screw.")
            print(f"Speed = (Distance) / {total_time:.2f}")

if __name__ == "__main__":
    calibrate()
