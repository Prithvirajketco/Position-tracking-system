import time
import nidaqmx
import config
from nidaqmx.constants import TerminalConfiguration

def scan_ai_channels():
    print("--- EMS 2 AI Channel Scanner ---")
    print(f"Scanning module: {config.MOD_AI}")
    print("Move your hand in front of the sensor and watch for changing numbers.\n")
    
    with nidaqmx.Task() as task:
        # Adding first 8 channels to find the active one
        num_channels = 8
        for i in range(num_channels):
            try:
                task.ai_channels.add_ai_voltage_chan(
                    f"{config.MOD_AI}/ai{i}",
                    terminal_config=TerminalConfiguration.DIFF
                )
            except Exception as e:
                num_channels = i
                break
        
        print(f"Monitoring {num_channels} channels (ai0 through ai{num_channels-1})...")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                data = task.read()
                # Print all channel values on one line
                output = " | ".join([f"ai{i}: {val:6.3f}V" for i, val in enumerate(data)])
                print(output, end='\r')
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n\nScan stopped.")

if __name__ == "__main__":
    scan_ai_channels()
