require("dotenv").config();
const http = require("http");
const { spawn } = require("child_process");
const path = require("path");

const PORT       = parseInt(process.env.PORT || "3000", 10);
const SCRIPTS_DIR = process.env.SCRIPTS_DIR || path.join(__dirname, "scripts");

let tvState = "OFF";
let busy    = false;

// ── HTTP Server ───────────────────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  const url = req.url.toLowerCase();

  // GET /status — current state
  if (req.method === "GET" && url === "/status") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ state: tvState, busy }));
  }

  // POST /on
  if (req.method === "POST" && url === "/on") {
    if (busy) {
      res.writeHead(409, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ error: "Command already running" }));
    }
    runScript("tv-on.ps1", "ON");
    res.writeHead(202, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ status: "accepted", command: "ON" }));
  }

  // POST /off
  if (req.method === "POST" && url === "/off") {
    if (busy) {
      res.writeHead(409, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ error: "Command already running" }));
    }
    runScript("tv-off.ps1", "OFF");
    res.writeHead(202, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ status: "accepted", command: "OFF" }));
  }

  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, () => {
  console.log(`[HTTP] TV Remote server listening on port ${PORT}`);
  console.log(`  POST http://YOUR_PC_IP:${PORT}/on`);
  console.log(`  POST http://YOUR_PC_IP:${PORT}/off`);
  console.log(`  GET  http://YOUR_PC_IP:${PORT}/status`);
});

// ── PowerShell runner ─────────────────────────────────────────────────────────
function runScript(scriptFile, targetState) {
  const scriptPath = path.join(SCRIPTS_DIR, scriptFile);
  console.log(`[TV] Running ${scriptFile}`);
  busy = true;

  const ps = spawn("powershell.exe", [
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", scriptPath,
  ]);

  ps.stdout.on("data", (d) => process.stdout.write(`[PS] ${d}`));
  ps.stderr.on("data", (d) => process.stderr.write(`[PS ERR] ${d}`));

  ps.on("close", (code) => {
    busy = false;
    tvState = code === 0 ? targetState : tvState;
    console.log(`[TV] Done — state: ${tvState} (exit code ${code})`);
  });

  ps.on("error", (err) => {
    busy = false;
    console.error("[TV] Failed to start PowerShell:", err.message);
  });
}
