import nidaqmx
import config
import time

def test_motor():
    print("--- EMS 2 Motor Test Utility ---")
    print(f"Testing DO Module: {config.MOD_DO}")
    print("This will pulse IN1, IN2, and PWM for 2 seconds each.")
    
    try:
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(config.DO_MOTOR_IN1)
            task.do_channels.add_do_chan(config.DO_MOTOR_IN2)
            task.do_channels.add_do_chan(config.DO_MOTOR_PWM)

            print("\n1. Pulsing IN1 (Direction 1)...")
            task.write([True, False, False])
            time.sleep(2)
            
            print("2. Pulsing IN2 (Direction 2)...")
            task.write([False, True, False])
            time.sleep(2)
            
            print("3. Pulsing PWM (Enable)...")
            task.write([False, False, True])
            time.sleep(2)

            print("4. All ON (Attempting Movement)...")
            task.write([True, False, True])
            time.sleep(2)

            print("\nTest complete. All outputs OFF.")
            task.write([False, False, False])

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_motor()
