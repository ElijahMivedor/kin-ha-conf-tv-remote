require("dotenv").config();
const http = require("http");
const { spawn } = require("child_process");
const path = require("path");

const PORT        = parseInt(process.env.PORT || "2025", 10);
const SCRIPTS_DIR = process.env.SCRIPTS_DIR || path.join(__dirname, "scripts");

let tvState = "OFF";
let busy    = false;

// ── HTTP Server ───────────────────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  const url = req.url.toLowerCase();

  // GET /status
  if (req.method === "GET" && url === "/status") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ state: tvState, busy }));
  }

  // POST /on
  if (req.method === "POST" && url === "/on") {
    if (busy) return rejectBusy(res);
    runScript("tv-on.ps1", "ON");
    return accept(res, "ON");
  }

  // POST /off
  if (req.method === "POST" && url === "/off") {
    if (busy) return rejectBusy(res);
    runScript("tv-off.ps1", "OFF");
    return accept(res, "OFF");
  }

  // POST /toggle
  if (req.method === "POST" && url === "/toggle") {
    if (busy) return rejectBusy(res);
    if (tvState === "ON") {
      runScript("tv-off.ps1", "OFF");
      return accept(res, "OFF");
    } else {
      runScript("tv-on.ps1", "ON");
      return accept(res, "ON");
    }
  }

  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, () => {
  console.log(`[HTTP] TV Remote server listening on port ${PORT}`);
  console.log(`  POST http://YOUR_PC_IP:${PORT}/on`);
  console.log(`  POST http://YOUR_PC_IP:${PORT}/off`);
  console.log(`  POST http://YOUR_PC_IP:${PORT}/toggle`);
  console.log(`  GET  http://YOUR_PC_IP:${PORT}/status`);
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function accept(res, command) {
  res.writeHead(202, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ status: "accepted", command }));
}

function rejectBusy(res) {
  res.writeHead(409, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Command already running" }));
}

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
