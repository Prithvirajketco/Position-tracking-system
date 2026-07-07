import time
import config
from daq_interface import DAQInterface

def calibrate_ir():
    print("--- EMS 2 IR Sensor Calibration Tool (v4) ---")
    print("Mode: DIFF (Differential). Ensure wiring is correct!")
    print("\nPress Ctrl+C to exit.\n")
    
    with DAQInterface(simulation=config.SIMULATION_MODE) as daq:
        try:
            while True:
                voltage = daq.read_sensor_voltage()
                
                # Baseline calculation
                try:
                    if voltage > 0.01:
                        raw_dist = 29.988 * (voltage ** -1.173)
                    else:
                        raw_dist = 0.0
                except:
                    raw_dist = -1.0
                
                print(f"Voltage: {voltage:8.4f} V | Raw Code Value: {raw_dist:8.2f}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nExiting Calibration Tool.")

if __name__ == "__main__":
    calibrate_ir()
