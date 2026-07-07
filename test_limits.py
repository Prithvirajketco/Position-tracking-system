import time
import config
from daq_interface import DAQInterface

def test_limits():
    print("--- EMS 2 Limit Switch Tester ---")
    print("Unpressed switches should usually be 'True'.")
    print("Press a switch to see if it changes to 'False'.\n")
    
    with DAQInterface(simulation=config.SIMULATION_MODE) as daq:
        try:
            while True:
                limits = daq.read_limit_switches()
                # Use str() to ensure clear visibility
                l1 = "PRESSED" if not limits[0] else "OPEN   "
                l2 = "PRESSED" if not limits[1] else "OPEN   "
                print(f"L1 (Home): {limits[0]} ({l1}) | L2 (End): {limits[1]} ({l2})", end='\r')
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nTest Stopped.")

if __name__ == "__main__":
    test_limits()
