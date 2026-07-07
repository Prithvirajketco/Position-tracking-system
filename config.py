# --- MODULE CONFIGURATION ---
# Module names as seen in NI MAX (Updated from cDAQ1 to cDAQ2)
MOD_AI = "cDAQ2Mod8"
MOD_DI = "cDAQ2Mod2"
MOD_DO = "cDAQ2Mod5"

# --- CHANNEL DEFINITIONS ---
# Analog Input (IR Sensor)
AI_IR_SENSOR = f"{MOD_AI}/ai0"

# Digital Inputs (Limit Switches)
DI_LIMIT_HOME = f"{MOD_DI}/port0/line1"
DI_LIMIT_END  = f"{MOD_DI}/port0/line0"

# Digital Outputs (Motor Driver)
DO_MOTOR_IN1 = f"{MOD_DO}/port0/line0"
DO_MOTOR_IN2 = f"{MOD_DO}/port0/line1"
DO_MOTOR_PWM = f"{MOD_DO}/port0/line2"

# --- CONTROL PARAMETERS ---
TARGET_DISTANCE_CM = 15.0
TOLERANCE_CM = 0.5
K_PROP = 0.2
LOOP_INTERVAL = 0.05  # 20Hz

# --- SYSTEM SETTINGS ---
SIMULATION_MODE = False  # Set to True to test without hardware

# --- CALIBRATION DATA ---
# Update this after running calibrate.py
LEAD_SCREW_SPEED_CMS = 0.46  # cm/sec