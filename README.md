# Position Tracking System (EMS 2 Record & Mimic)

A Python-based hardware control and data acquisition system designed to record object positions using an IR sensor and mimic those movements using a motorized linear actuator (lead screw). 

## 🎯 Overview
The **EMS 2 Record & Mimic System** allows a user to manually move an object to a new position, capture that position using an analog IR sensor, and then automatically drive a motor to mimic that exact movement distance and direction. It features both a command-line interface for direct terminal control and a rich web-based GUI via FastAPI and WebSockets.

## 🛠 Hardware Requirements
- **Data Acquisition (DAQ)**: National Instruments cDAQ chassis with appropriate modules (configured for `cDAQ2`).
- **Sensors**: IR distance sensor (Analog Input).
- **Actuators**: Motor driver connected to a lead-screw linear actuator (Digital Output for IN1, IN2, PWM).
- **Safety**: Two limit switches (Home and End) for safety bounds (Digital Input).

## 💻 Software Setup

### Prerequisites
- Python 3.7+
- NI-DAQmx drivers installed on the host system (NI MAX).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Prithvirajketco/Position-tracking-system.git
   cd Position-tracking-system
   ```
2. Install the required Python packages (we recommend using a virtual environment):
   ```bash
   pip install nidaqmx fastapi uvicorn websockets pydantic
   ```

## ⚙️ Configuration
All hardware channels and system parameters are defined in `config.py`. Update these values to match your specific NI MAX setup:
- `MOD_AI`, `MOD_DI`, `MOD_DO`: Your cDAQ module names.
- `SIMULATION_MODE`: Set to `True` to test the software without physical DAQ hardware connected.
- `LEAD_SCREW_SPEED_CMS`: Calibrated motor speed (run `calibrate.py` to update this).

## 🚀 Usage

### Option 1: Web GUI (Recommended)
Launch the FastAPI web server to control and monitor the system via a browser-based dashboard:
```bash
python gui_server.py
```
Then, open `http://localhost:8000` in your web browser. You can monitor telemetry, perform homing, move the motor manually, and use the Record & Mimic functionality.

### Option 2: Command Line Interface
Run the main CLI application to interact directly via the terminal:
```bash
python main.py
```
Follow the terminal prompts to capture new positions and execute mimic movements.

## 📁 Project Structure
- `main.py`: CLI-based application logic for Record & Mimic.
- `gui_server.py`: FastAPI server serving the web GUI and WebSocket telemetry.
- `daq_interface.py`: Abstraction layer for `nidaqmx` hardware interactions.
- `controller.py`: Logic for calculating distances and travel times.
- `config.py`: Hardware mappings and system settings.
- `calibrate*.py`: Utilities for calibrating the IR sensor and motor speed.
- `static/`: HTML, CSS, and JS files for the web GUI.

## 📜 License
MIT License
