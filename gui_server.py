import asyncio
import logging
import json
import time
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import config
from daq_interface import DAQInterface
from controller import Controller

# --- LOGGING SETUP ---
class WebSocketHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.clients: List[WebSocket] = []

    def emit(self, record):
        log_entry = self.format(record)
        message = json.dumps({"type": "log", "data": log_entry})
        # We can't use await here, so we'll push to a queue or use a background loop
        # For simplicity in this script, we'll let the main loop handle the broadcast
        asyncio.create_task(self.broadcast(message))

    async def broadcast(self, message):
        for client in self.clients:
            try:
                await client.send_text(message)
            except:
                pass

ws_log_handler = WebSocketHandler()
ws_log_handler.setFormatter(logging.Formatter('%(message)s'))

logger = logging.getLogger("EMS2")
logger.setLevel(logging.INFO)
logger.addHandler(ws_log_handler)
# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console_handler)

# --- APP SETUP ---
app = FastAPI()
daq = DAQInterface(simulation=config.SIMULATION_MODE)
ctrl = Controller()

# Global state
class SystemState:
    def __init__(self):
        self.is_running_mimic = False
        self.last_dist = 5.0
        self.current_mode = "IDLE"
        self.telemetry = {
            "voltage": 0.0,
            "distance": 0.0,
            "limits": [True, True],
            "motor": [False, False, False]
        }
        self.mimic_info = {
            "current_pos": 5.0,
            "new_pos": 5.0,
            "distance": 0.0,
            "est_time": 0.0
        }

state = SystemState()

# --- BACKGROUND TASKS ---
async def telemetry_loop():
    """Reads sensor data and broadcasts via WebSocket."""
    while True:
        try:
            v = await asyncio.to_thread(daq.read_sensor_voltage)
            d = ctrl.get_distance(v)
            l = await asyncio.to_thread(daq.read_limit_switches)
            m = daq._last_motor_state or [False, False, False]
            
            state.telemetry = {
                "voltage": round(v, 4),
                "distance": round(d, 2),
                "limits": l,
                "motor": m
            }
            
            # Broadcast telemetry to all connected clients
            message = json.dumps({"type": "telemetry", "data": state.telemetry})
            await ws_log_handler.broadcast(message)
            
        except Exception as e:
            logger.error(f"Telemetry error: {e}")
        
        await asyncio.sleep(0.1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(telemetry_loop())
    
    # Replicate main.py header
    logger.info("--- EMS 2 Record & Mimic System ---")
    logger.info(f"Calibrated Speed: {config.LEAD_SCREW_SPEED_CMS} cm/s")
    logger.info(f"Simulation Mode: {config.SIMULATION_MODE}")
    logger.info("-----------------------------------")
    
    logger.info(f"System Initialized at {state.last_dist:.2f} cm")
    logger.info(f"READY: Move the object to NEW position and click [CAPTURE POSITION].")
    logger.info(f"(Reference position: {state.last_dist:.2f} cm)")

@app.on_event("shutdown")
def shutdown_event():
    daq.stop_motor()
    daq.close()
    logger.info("Shutting down...")

# --- API ENDPOINTS ---
class Command(BaseModel):
    action: str # forward, backward, stop, mimic_start, mimic_stop, home, calibrate

@app.post("/control")
async def control_motor(cmd: Command):
    if cmd.action == "forward":
        state.current_mode = "MANUAL_FWD"
        logger.info("Moving Forward...")
        asyncio.create_task(move_until_limit("FORWARD"))
    
    elif cmd.action == "backward":
        state.current_mode = "MANUAL_BWD"
        logger.info("Moving Backward...")
        asyncio.create_task(move_until_limit("BACKWARD"))
    
    elif cmd.action == "stop":
        state.is_running_mimic = False
        state.current_mode = "IDLE"
        await asyncio.to_thread(daq.stop_motor)
        logger.info("Motor Stopped.")
    
    elif cmd.action == "home":
        state.current_mode = "HOMING"
        asyncio.create_task(run_homing())

    elif cmd.action == "mimic_start":
        state.is_running_mimic = True
        state.current_mode = "MIMIC"
        logger.info("Record & Mimic Mode Active. Waiting for movement...")
        # Handled in a separate logic or loop? 
        # Actually, let's just trigger a "capture" event from the UI instead of a loop
        # The user requested "all prompts from the terminal", 
        # which means I should mimic the main.py workflow.
    
    elif cmd.action == "capture":
        if state.current_mode == "MIMIC":
            asyncio.create_task(process_mimic_step())

    return {"status": "ok", "mode": state.current_mode}

async def move_until_limit(direction):
    try:
        while state.current_mode.startswith("MANUAL"):
            limits = await asyncio.to_thread(daq.read_limit_switches)
            if direction == "FORWARD" and not limits[1]:
                logger.info("Reached Limit 2 (End).")
                break
            if direction == "BACKWARD" and not limits[0]:
                logger.info("Reached Limit 1 (Home).")
                break
            
            if direction == "FORWARD":
                await asyncio.to_thread(daq.set_motor, True, False, True)
            else:
                await asyncio.to_thread(daq.set_motor, False, True, True)
            
            await asyncio.sleep(0.05)
    finally:
        await asyncio.to_thread(daq.stop_motor)
        if state.current_mode.startswith("MANUAL"):
            state.current_mode = "IDLE"

async def run_homing():
    logger.info("Homing sequence started...")
    await asyncio.to_thread(daq.home_motor)
    state.current_mode = "IDLE"
    logger.info("Homing complete.")

async def process_mimic_step():
    v_end = await asyncio.to_thread(daq.read_sensor_voltage)
    current_dist = ctrl.get_distance(v_end)
    logger.info(f"Captured New Position: {current_dist:.2f} cm")

    displacement = current_dist - state.last_dist
    dist = abs(displacement)
    direction = "FORWARD" if displacement > 0 else "BACKWARD"
    travel_time = ctrl.get_travel_time(dist)

    # Update state and broadcast to UI
    state.mimic_info = {
        "current_pos": round(state.last_dist, 2),
        "new_pos": round(current_dist, 2),
        "distance": round(dist, 2),
        "est_time": round(travel_time, 2)
    }
    await ws_log_handler.broadcast(json.dumps({"type": "mimic_info", "data": state.mimic_info}))

    if dist < 0.1:
        logger.info("No significant movement detected.")
        return

    logger.info(f"ACTION: Mimicking {dist:.2f} cm {direction}... Est. Time: {travel_time:.2f}s")
    
    start_time = time.time()
    try:
        while (time.time() - start_time) < travel_time:
            limits = await asyncio.to_thread(daq.read_limit_switches)
            if (direction == "BACKWARD" and not limits[0]) or \
               (direction == "FORWARD" and not limits[1]):
                logger.warning(f"SAFETY STOP: Hit {direction} limit switch!")
                break
            
            if direction == "FORWARD":
                await asyncio.to_thread(daq.set_motor, True, False, True)
            else:
                await asyncio.to_thread(daq.set_motor, False, True, True)
            await asyncio.sleep(0.05)
    finally:
        await asyncio.to_thread(daq.stop_motor)
        state.last_dist = current_dist
        # Update current position for UI after move
        state.mimic_info["current_pos"] = round(state.last_dist, 2)
        await ws_log_handler.broadcast(json.dumps({"type": "mimic_info", "data": state.mimic_info}))
        
        logger.info("Movement Complete.")
        logger.info("-" * 30)
        logger.info(f"READY: Move the object to NEW position and click [CAPTURE POSITION].")
        logger.info(f"(Reference position: {state.last_dist:.2f} cm)")

# --- WEBSOCKET ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_log_handler.clients.append(websocket)
    try:
        while True:
            # Just keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_log_handler.clients.remove(websocket)

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
