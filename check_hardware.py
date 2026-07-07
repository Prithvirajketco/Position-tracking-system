import nidaqmx
try:
    system = nidaqmx.system.System.local()
    print("\n--- NI-DAQmx Device Discovery ---")
    if not system.devices:
        print("No NI-DAQ devices detected! Check USB/Network connection.")
    for device in system.devices:
        print(f"Device: {device.name}")
        print(f"  Product: {device.product_type}")
        print(f"  AI Channels: {len(device.ai_physical_chans)}")
        print(f"  DI Channels: {len(device.di_lines)}")
        print(f"  DO Channels: {len(device.do_lines)}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
