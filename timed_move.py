
import time
import config
from daq_interface import DAQInterface
from controller import Controller

def timed_move():
    print("--- 5cm Timed Movement Test ---")
    print("This will ignore limits and move 5cm away from the motor.")
    
    with DAQInterface(simulation=False) as daq:
        ctrl = Controller()
        
        # Get starting position
        start_dist = ctrl.get_distance(daq.read_sensor_voltage())
        print(f"Starting Distance: {start_dist:.2f} cm")
        
        print("\nMoving Forward (Away from Motor)...")
        start_time = time.time()
        
        try:
            while True:
                current_dist = ctrl.get_distance(daq.read_sensor_voltage())
                moved_dist = abs(current_dist - start_dist)
                
                print(f"\rMoved: {moved_dist:.2f} cm", end="")
                
                if moved_dist >= 5.0:
                    daq.stop_motor()
                    end_time = time.time()
                    print("\n\nTarget Reached (5cm).")
                    break
                
                # Move Forward
                daq.set_motor(True, False, True)
                time.sleep(0.05)
                
            total_time = end_time - start_time
            print(f"Time Taken for 5cm: {total_time:.2f} seconds")
            print(f"Calculated Speed   : {5.0 / total_time:.4f} cm/sec")
            
        except KeyboardInterrupt:
            daq.stop_motor()
            print("\nStopped by user.")

if __name__ == "__main__":
    timed_move()
