# TV Remote — RS232 via MQTT

Controls a Sharp Aquos TV (RS232 / serial) from Home Assistant via a Node.js MQTT bridge running on a Windows PC.

## Architecture

```
Home Assistant (HACS switch)
        ↕  MQTT
Node.js server (Windows PC)
        ↕  PowerShell → COM4 RS232
        TV
```

## Setup

### 1. Node.js Server (Windows PC with TV attached)

```bash
cd server
copy .env.example .env   # then edit .env with your MQTT broker IP
npm install
node index.js
```

The server subscribes to `tv_remote/set` and publishes state to `tv_remote/state`.

### 2. Home Assistant HACS Integration

1. Add this repository to HACS as a custom integration repository.
2. Install **TV Remote (RS232 via MQTT)**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration → TV Remote**.
5. Enter the same topics used in your `.env` (defaults work if unchanged).

Make sure the **MQTT integration** is already configured in HA (Mosquitto or any broker).

## MQTT Topics

| Topic           | Direction      | Payload                          |
|-----------------|----------------|----------------------------------|
| `tv_remote/set` | HA → server    | `ON` or `OFF`                    |
| `tv_remote/state` | server → HA  | `ON`, `OFF`, `TRANSITIONING`, `OFFLINE` |

## PowerShell Scripts

- `server/scripts/tv-on.ps1`  — powers on + switches to HDMI 1
- `server/scripts/tv-off.ps1` — powers off

Edit `COM4` in the scripts if your serial adapter is on a different port.
Run `[System.IO.Ports.SerialPort]::GetPortNames()` in PowerShell to list available ports.
