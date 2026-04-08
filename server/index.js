require("dotenv").config();
const mqtt = require("mqtt");
const { spawn } = require("child_process");
const path = require("path");

// ── Config ────────────────────────────────────────────────────────────────────
const MQTT_HOST     = process.env.MQTT_HOST     || "localhost";
const MQTT_PORT     = parseInt(process.env.MQTT_PORT || "1883", 10);
const MQTT_USERNAME = process.env.MQTT_USERNAME || undefined;
const MQTT_PASSWORD = process.env.MQTT_PASSWORD || undefined;
const COMMAND_TOPIC = process.env.COMMAND_TOPIC || "tv_remote/set";
const STATE_TOPIC   = process.env.STATE_TOPIC   || "tv_remote/state";
const SCRIPTS_DIR   = process.env.SCRIPTS_DIR   || path.join(__dirname, "scripts");

// ── State ─────────────────────────────────────────────────────────────────────
let tvState = "OFF";   // last known state
let busy    = false;   // prevent overlapping commands

// ── MQTT ──────────────────────────────────────────────────────────────────────
const client = mqtt.connect(`mqtt://${MQTT_HOST}:${MQTT_PORT}`, {
  username: MQTT_USERNAME,
  password: MQTT_PASSWORD,
  clientId: `tv-remote-${Math.random().toString(16).slice(2, 8)}`,
  will: {
    topic: STATE_TOPIC,
    payload: "OFFLINE",
    retain: true,
  },
});

client.on("connect", () => {
  console.log(`[MQTT] Connected to ${MQTT_HOST}:${MQTT_PORT}`);
  client.subscribe(COMMAND_TOPIC, (err) => {
    if (err) return console.error("[MQTT] Subscribe error:", err.message);
    console.log(`[MQTT] Subscribed to ${COMMAND_TOPIC}`);
  });
  // Announce current state on (re)connect
  publishState(tvState);
});

client.on("message", (topic, payload) => {
  const command = payload.toString().trim().toUpperCase();
  console.log(`[MQTT] Received command: ${command}`);

  if (topic !== COMMAND_TOPIC) return;

  if (busy) {
    console.warn("[TV] Command ignored — previous command still running");
    return;
  }

  if (command === "ON")  return runScript("tv-on.ps1",  "ON");
  if (command === "OFF") return runScript("tv-off.ps1", "OFF");

  console.warn(`[TV] Unknown command: ${command}`);
});

client.on("error", (err) => console.error("[MQTT] Error:", err.message));
client.on("reconnect", () => console.log("[MQTT] Reconnecting..."));

// ── PowerShell runner ─────────────────────────────────────────────────────────
function runScript(scriptFile, targetState) {
  const scriptPath = path.join(SCRIPTS_DIR, scriptFile);
  console.log(`[TV] Running ${scriptFile} → state will be ${targetState}`);

  busy = true;
  publishState("TRANSITIONING");

  const ps = spawn("powershell.exe", [
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", scriptPath,
  ]);

  ps.stdout.on("data", (d) => process.stdout.write(`[PS] ${d}`));
  ps.stderr.on("data", (d) => process.stderr.write(`[PS ERR] ${d}`));

  ps.on("close", (code) => {
    busy = false;
    if (code === 0) {
      tvState = targetState;
      console.log(`[TV] Script finished OK — state: ${tvState}`);
    } else {
      console.error(`[TV] Script exited with code ${code}`);
    }
    publishState(tvState);
  });

  ps.on("error", (err) => {
    busy = false;
    console.error("[TV] Failed to start PowerShell:", err.message);
    publishState(tvState);
  });
}

function publishState(state) {
  client.publish(STATE_TOPIC, state, { retain: true });
  console.log(`[MQTT] Published state: ${state}`);
}
