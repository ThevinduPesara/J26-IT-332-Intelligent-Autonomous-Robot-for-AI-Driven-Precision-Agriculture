export type ConnectionState = "disconnected" | "connecting" | "connected" | "error";
export type MovementCommand = "LEFT" | "RIGHT" | "STOP";

export interface Esp32StatusResponse {
  connected: boolean;
  wifiConnected: boolean;
  ip: string;
  wifiRSSI: number;
  uptime: number;
  motorRunning: boolean;
  motorDirection: "LEFT" | "RIGHT" | string;
  status: string;
}

export interface CableRobotServiceCallbacks {
  onConnectionChange?: (state: ConnectionState, message?: string) => void;
  onStatusUpdate?: (status: Esp32StatusResponse) => void;
  onError?: (err: Error) => void;
}

class CableRobotService {
  private esp32BaseUrl: string;
  private connectionState: ConnectionState = "disconnected";
  private callbacks: CableRobotServiceCallbacks = {};
  private activeCommand: MovementCommand = "STOP";
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private pollStatusTimer: NodeJS.Timeout | null = null;
  private isCommandInFlight: boolean = false;

  constructor() {
    const rawUrl =
      process.env.NEXT_PUBLIC_ESP32_URL || "http://192.168.8.107";
    this.esp32BaseUrl = this.normalizeUrl(rawUrl);
  }

  private normalizeUrl(url: string): string {
    let clean = url.trim();
    if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
      clean = `http://${clean}`;
    }
    return clean.replace(/\/+$/, "");
  }

  public setCallbacks(callbacks: CableRobotServiceCallbacks) {
    this.callbacks = callbacks;
  }

  public getBaseUrl(): string {
    return this.esp32BaseUrl;
  }

  public setBaseUrl(newUrl: string) {
    this.esp32BaseUrl = this.normalizeUrl(newUrl);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem("agribot_esp32_url", this.esp32BaseUrl);
      } catch {
        // Fallback
      }
    }
    this.checkStatus();
  }

  public getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  public isConnected(): boolean {
    return this.connectionState === "connected";
  }

  /**
   * Start polling ESP32 status (/api/status)
   */
  public start(customUrl?: string) {
    if (typeof window === "undefined") return;

    if (customUrl) {
      this.esp32BaseUrl = this.normalizeUrl(customUrl);
    } else {
      try {
        const saved = localStorage.getItem("agribot_esp32_url");
        if (saved) this.esp32BaseUrl = this.normalizeUrl(saved);
      } catch {
        // Fallback
      }
    }

    this.checkStatus();

    // Poll status every 2 seconds
    if (!this.pollStatusTimer) {
      this.pollStatusTimer = setInterval(() => {
        this.checkStatus();
      }, 2000);
    }
  }

  public stop() {
    this.stopMovement();
    if (this.pollStatusTimer) {
      clearInterval(this.pollStatusTimer);
      this.pollStatusTimer = null;
    }
  }

  /**
   * Ping GET /api/status on ESP32
   */
  public async checkStatus(): Promise<Esp32StatusResponse | null> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1800);

      const res = await fetch(`${this.esp32BaseUrl}/api/status`, {
        method: "GET",
        signal: controller.signal,
        cache: "no-store",
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: Esp32StatusResponse = await res.json();

      if (this.connectionState !== "connected") {
        this.connectionState = "connected";
        this.callbacks.onConnectionChange?.("connected", `ESP32 Online (${data.ip})`);
      }

      this.callbacks.onStatusUpdate?.(data);
      return data;
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : "ESP32 Offline";
      if (this.connectionState !== "disconnected") {
        this.connectionState = "disconnected";
        this.callbacks.onConnectionChange?.("disconnected", `ESP32 Disconnected (${errMsg})`);
      }
      return null;
    }
  }

  /**
   * Send single command: POST /api/command with body "LEFT" | "RIGHT" | "STOP"
   */
  public async sendCommand(cmd: MovementCommand): Promise<boolean> {
    try {
      this.isCommandInFlight = true;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);

      // Send to /api/command with query param ?cmd=LEFT as well as body
      const url = `${this.esp32BaseUrl}/api/command?cmd=${cmd}`;
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "text/plain",
        },
        body: cmd,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      this.isCommandInFlight = false;
      return res.ok;
    } catch {
      this.isCommandInFlight = false;
      return false;
    }
  }

  /**
   * Continuous movement loop (every 250ms heartbeat)
   * Prevents ESP32 COMMAND_TIMEOUT_MS (700ms) safety timeout while held down.
   */
  public async startContinuousMovement(direction: "LEFT" | "RIGHT"): Promise<boolean> {
    this.activeCommand = direction;

    // Send first pulse immediately
    const ok = await this.sendCommand(direction);
    if (!ok) return false;

    this.stopMovementHeartbeat();

    // 250ms periodic keep-alive heartbeat while button is held
    this.heartbeatTimer = setInterval(async () => {
      if (
        this.activeCommand === "LEFT" ||
        this.activeCommand === "RIGHT"
      ) {
        if (!this.isCommandInFlight) {
          await this.sendCommand(this.activeCommand);
        }
      } else {
        this.stopMovementHeartbeat();
      }
    }, 250);

    return true;
  }

  /**
   * Immediately stops motor and clears heartbeat
   */
  public async stopMovement(): Promise<boolean> {
    this.activeCommand = "STOP";
    this.stopMovementHeartbeat();
    return await this.sendCommand("STOP");
  }

  private stopMovementHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  public getActiveCommand(): MovementCommand {
    return this.activeCommand;
  }
}

export const cableRobotService = new CableRobotService();
export default cableRobotService;
