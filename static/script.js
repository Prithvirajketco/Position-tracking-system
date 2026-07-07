const elements = {
    voltage: document.getElementById('val-voltage'),
    distance: document.getElementById('val-distance'),
    limitHome: document.getElementById('limit-home'),
    limitEnd: document.getElementById('limit-end'),
    systemStatus: document.getElementById('system-status'),
    logContainer: document.getElementById('log-container'),
    btnForward: document.getElementById('btn-forward'),
    btnBackward: document.getElementById('btn-backward'),
    btnStop: document.getElementById('btn-stop'),
    btnHome: document.getElementById('btn-home'),
    btnMimic: document.getElementById('btn-mimic'),
    btnCapture: document.getElementById('btn-capture'),
    cardMimic: document.getElementById('card-mimic-info'),
    mimicCurrent: document.getElementById('mimic-current'),
    mimicNew: document.getElementById('mimic-new'),
    mimicDist: document.getElementById('mimic-dist'),
    mimicTime: document.getElementById('mimic-time')
};

let isMimicMode = false;

// --- WEBSOCKET CONNECTION ---
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    
    if (msg.type === 'telemetry') {
        updateTelemetry(msg.data);
    } else if (msg.type === 'log') {
        addLog(msg.data);
    } else if (msg.type === 'mimic_info') {
        updateMimicInfo(msg.data);
    }
};

function updateTelemetry(data) {
    elements.voltage.innerText = data.voltage.toFixed(3);
    elements.distance.innerText = data.distance.toFixed(1);
    
    // Update Limits
    // data.limits[0] is Home. False = Pressed.
    updateLimit(elements.limitHome, !data.limits[0]);
    updateLimit(elements.limitEnd, !data.limits[1]);
}

function updateLimit(el, isActive) {
    if (isActive) {
        el.classList.add('active');
        el.classList.remove('ok');
    } else {
        el.classList.remove('active');
        el.classList.add('ok');
    }
}

function updateMimicInfo(data) {
    elements.cardMimic.style.opacity = "1";
    elements.cardMimic.style.borderColor = "var(--primary)";
    
    elements.mimicCurrent.innerText = data.current_pos.toFixed(1);
    elements.mimicNew.innerText = data.new_pos.toFixed(1);
    elements.mimicDist.innerText = data.distance.toFixed(1);
    elements.mimicTime.innerText = data.est_time.toFixed(1);

    // Optional: add a glow effect to the card when updated
    elements.cardMimic.style.boxShadow = "0 0 20px var(--primary-glow)";
    setTimeout(() => {
        elements.cardMimic.style.boxShadow = "0 8px 32px rgba(0, 0, 0, 0.3)";
    }, 500);
}

function addLog(text) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    if (text.includes('ERROR')) entry.classList.add('error');
    if (text.includes('INFO')) entry.classList.add('info');
    entry.innerText = text;
    elements.logContainer.appendChild(entry);
    elements.logContainer.scrollTop = elements.logContainer.scrollHeight;
}

// --- API CALLS ---
async function sendCommand(action) {
    try {
        const response = await fetch('/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        const data = await response.json();
        elements.systemStatus.innerText = data.mode;
        return data;
    } catch (error) {
        addLog(`[UI ERROR] Failed to send command ${action}: ${error}`);
    }
}

// --- EVENT LISTENERS ---
elements.btnForward.addEventListener('mousedown', () => sendCommand('forward'));
elements.btnBackward.addEventListener('mousedown', () => sendCommand('backward'));
elements.btnStop.addEventListener('click', () => {
    sendCommand('stop');
    if (isMimicMode) toggleMimicMode();
});

// For safety, stop motor on mouseup
window.addEventListener('mouseup', () => {
    // Only stop if we were in manual mode
    if (elements.systemStatus.innerText.startsWith('MANUAL')) {
        sendCommand('stop');
    }
});

elements.btnHome.addEventListener('click', () => sendCommand('home'));

elements.btnMimic.addEventListener('click', toggleMimicMode);
elements.btnCapture.addEventListener('click', () => sendCommand('capture'));

function toggleMimicMode() {
    isMimicMode = !isMimicMode;
    const statusLabel = elements.btnMimic.querySelector('.mode-status');
    
    if (isMimicMode) {
        sendCommand('mimic_start');
        statusLabel.innerText = 'ACTIVE';
        elements.btnMimic.style.borderColor = 'var(--primary)';
        elements.btnCapture.style.display = 'block';
    } else {
        sendCommand('mimic_stop');
        statusLabel.innerText = 'INACTIVE';
        elements.btnMimic.style.borderColor = 'var(--card-border)';
        elements.btnCapture.style.display = 'none';
    }
}

addLog("System Initialized. Ready for commands.");
