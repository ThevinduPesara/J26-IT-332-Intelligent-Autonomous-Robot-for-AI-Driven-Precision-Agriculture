// Standalone MQTT Broker supporting both TCP (1883) for ESP32 and WebSocket (9001) for Web Browser
const aedes = require("aedes")();
const net = require("net");
const http = require("http");
const ws = require("websocket-stream");

const TCP_PORT = 1883;
const WS_PORT = 9001;

// 1. TCP Server for ESP32 (Port 1883)
const tcpServer = net.createServer(aedes.handle);
tcpServer.listen(TCP_PORT, "0.0.0.0", () => {
  console.log(`[MQTT Broker] TCP listening on port ${TCP_PORT} (for ESP32)`);
});

// 2. WebSocket Server for Web Browser / Next.js (Port 9001)
const httpServer = http.createServer();
ws.createServer({ server: httpServer }, aedes.handle);
httpServer.listen(WS_PORT, "0.0.0.0", () => {
  console.log(`[MQTT Broker] WebSocket listening on port ${WS_PORT} (for Browser Dashboard)`);
  console.log(`[MQTT Broker] READY! Connect Dashboard & ESP32.`);
});

// Event Logging
aedes.on("client", (client) => {
  console.log(`[MQTT Broker] Client connected: ${client ? client.id : "unknown"}`);
});

aedes.on("clientDisconnect", (client) => {
  console.log(`[MQTT Broker] Client disconnected: ${client ? client.id : "unknown"}`);
});

aedes.on("publish", (packet, client) => {
  if (client) {
    console.log(`[MQTT Broker] ${client.id} -> ${packet.topic}: ${packet.payload.toString()}`);
  }
});
