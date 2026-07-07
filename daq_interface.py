import nidaqmx
from nidaqmx.constants import (LineGrouping, Edge, AcquisitionType, VoltageUnits, TerminalConfiguration)
import config

class DAQInterface:
    def __init__(self, simulation=False):
        self.simulation = simulation
        self.task_ai = None
        self.task_di = None
        self.task_do = None
        self._last_motor_state = None
        
        if not self.simulation:
            self._setup_tasks()

    def _setup_tasks(self):
        # 1. Analog Input Task
        self.task_ai = nidaqmx.Task()
        self.task_ai.ai_channels.add_ai_voltage_chan(
            config.AI_IR_SENSOR, 
            min_val=0.0, 
            max_val=5.0,
            terminal_config=TerminalConfiguration.DEFAULT
        )

        # 2. Digital Input Task
        self.task_di = nidaqmx.Task()
        self.task_di.di_channels.add_di_chan(config.DI_LIMIT_HOME)
        self.task_di.di_channels.add_di_chan(config.DI_LIMIT_END)

        # 3. Digital Output Task
        self.task_do = nidaqmx.Task()
        self.task_do.do_channels.add_do_chan(config.DO_MOTOR_IN1)
        self.task_do.do_channels.add_do_chan(config.DO_MOTOR_IN2)
        self.task_do.do_channels.add_do_chan(config.DO_MOTOR_PWM)



    def read_sensor_voltage(self):
        if self.simulation:
            return 1.5
        return self.task_ai.read()

    def read_limit_switches(self):
        if self.simulation:
            return [True, True]
        raw_values = self.task_di.read()
        # Invert logic: User says True=Pressed, so we return False for Pressed
        return [not val for val in raw_values]

    def set_motor(self, in1, in2, pwm):
        state = [bool(in1), bool(in2), bool(pwm)]
        
        if self.simulation:
            if state != self._last_motor_state:
                print(f"[SIM] Motor State Changed: {state}")
                self._last_motor_state = state
            return

        # Only update the hardware if the state has changed
        if state != self._last_motor_state:
            try:
                self.task_do.write(state)
                self._last_motor_state = state
                print(f"Motor Command Sent: {state}")
            except Exception as e:
                print(f"\n[ERROR] Motor Write Failed: {e}")

    def stop_motor(self):
        self.set_motor(False, False, False)

    def home_motor(self):
        """Moves the motor backward until the Home limit switch (Limit 1) is pressed."""
        print("\n[HOMING] Moving to Home switch (Limit 1)...")
        if self.simulation:
            print("[SIM] Homing sequence simulated.")
            return

        import time
        try:
            while True:
                limits = self.read_limit_switches()
                # limits[0] is Home (Backward Limit). False = Pressed.
                if not limits[0]:
                    break
                
                # Move Backward (Towards motor/sensor)
                self.set_motor(False, True, True)
                time.sleep(0.05)
        finally:
            self.stop_motor()
            print("[HOMING] Reached Limit 1 (Home). System Ready.")

    def close(self):
        if not self.simulation:
            if self.task_ai: self.task_ai.close()
            if self.task_di: self.task_di.close()
            if self.task_do: self.task_do.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_motor()
        self.close()
