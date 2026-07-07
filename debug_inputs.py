import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import config
import time

def debug():
    print("--- EMS 2 Advanced Hardware Scanner ---")
    print(f"Scanning AI channels on: {config.MOD_AI}")
    
    try:
        with nidaqmx.Task() as task_ai, \
             nidaqmx.Task() as task_di:

            # 1. Add all 4 channels of NI 9219 to see where the signal is
            for i in range(4):
                chan_path = f"{config.MOD_AI}/ai{i}"
                task_ai.ai_channels.add_ai_voltage_chan(
                    chan_path, 
                    min_val=-10.0, 
                    max_val=10.0,
                    terminal_config=TerminalConfiguration.DIFF
                )

            # 2. Setup Digital Inputs
            task_di.di_channels.add_di_chan(config.DI_LIMIT_HOME)
            task_di.di_channels.add_di_chan(config.DI_LIMIT_END)

            print("\nReading... Press Ctrl+C to stop.")
            print("CH0 (ai0) | CH1 (ai1) | CH2 (ai2) | CH3 (ai3) | Limits [H, E]")
            print("-" * 70)

            while True:
                voltages = task_ai.read()  # Returns a list of 4 voltages
                limits = task_di.read()
                
                v_str = " | ".join([f"{v:7.3f}V" for v in voltages])
                print(f"\r{v_str} | {limits}", end="")
                
                time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\nScanner stopped.")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nSuggestion: Check if 'cDAQ2Mod8' is the correct AI module in NI MAX.")

if __name__ == "__main__":
    debug()
