import time
import config
from daq_interface import DAQInterface

def manual_control():
    print("--- EMS 2 Manual Motor Control ---")
    print("Instructions:")
    print("  'f' + Enter : Move Forward (towards Limit 2)")
    print("  'b' + Enter : Move Backward (towards Limit 1)")
    print("  's' + Enter : Emergency Stop")
    print("  'q' + Enter : Quit")
    
    with DAQInterface(simulation=config.SIMULATION_MODE) as daq:
        try:
            while True:
                cmd = input("\nEnter Command (f/b/s/q): ").lower().strip()
                
                if cmd == 'q':
                    daq.stop_motor()
                    print("Exiting...")
                    break
                
                elif cmd == 's':
                    daq.stop_motor()
                    print("Motor Stopped.")
                
                elif cmd == 'f':
                    print("Moving Forward... (Press Ctrl+C to force stop)")
                    try:
                        while True:
                            limits = daq.read_limit_switches()
                            if not limits[1]: # Limit 2 pressed
                                daq.stop_motor()
                                print(">>> Reached Limit 2 (End).")
                                break
                            
                            daq.set_motor(True, False, True)
                            time.sleep(0.05)
                    except KeyboardInterrupt:
                        daq.stop_motor()
                        print("\nManual Stop triggered.")
                
                elif cmd == 'b':
                    print("Moving Backward... (Press Ctrl+C to force stop)")
                    try:
                        while True:
                            limits = daq.read_limit_switches()
                            if not limits[0]: # Limit 1 pressed
                                daq.stop_motor()
                                print(">>> Reached Limit 1 (Home).")
                                break
                            
                            daq.set_motor(False, True, True)
                            time.sleep(0.05)
                    except KeyboardInterrupt:
                        daq.stop_motor()
                        print("\nManual Stop triggered.")
                
                else:
                    print("Unknown command. Use f, b, s, or q.")
                    
        finally:
            daq.stop_motor()

if __name__ == "__main__":
    manual_control()
