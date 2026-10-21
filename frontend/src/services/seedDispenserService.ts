export type DispenserConnectionState = "disconnected" | "connecting" | "connected" | "error";

export interface DispenserStatusResponse {
  connected: boolean;
  wifiConnected: boolean;
  ip: string;
  wifiRSSI: number;
  uptime: number;
  dispenserActive: boolean;
  status: string;
}

export interface SeedDispenserCallbacks {
  onConnectionChange?: (state: DispenserConnectionState, message?: string) => void;
  onStatusUpdate?: (status: DispenserStatusResponse) => void;
  onError?: (err: Error) => void;
}

class SeedDispenserService {
  private esp32BaseUrl: string;
  private connectionState: DispenserConnectionState = "disconnected";
  private callbacks: SeedDispenserCallbacks = {};
  private pollStatusTimer: NodeJS.Timeout | null = null;
  private isCommandInFlight: boolean = false;
  private isDispenserActive: boolean = false;

  constructor() {
    const rawUrl =
      process.env.NEXT_PUBLIC_DISPENSER_ESP32_URL || "http://192.168.8.139";
    this.esp32BaseUrl = this.normalizeUrl(rawUrl);
  }

  private normalizeUrl(url: string): string {
    let clean = url.trim();
    if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
      clean = `http://${clean}`;
    }
    return clean.replace(/\/+$/, "");
  }

  public setCallbacks(callbacks: SeedDispenserCallbacks) {
    this.callbacks = callbacks;
  }

  public getBaseUrl(): string {
    return this.esp32BaseUrl;
  }

  public setBaseUrl(newUrl: string) {
    this.esp32BaseUrl = this.normalizeUrl(newUrl);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem("agribot_dispenser_url", this.esp32BaseUrl);
      } catch {
        // Fallback
      }
    }
    this.checkStatus();
  }

  public getConnectionState(): DispenserConnectionState {
    return this.connectionState;
  }

  public isConnected(): boolean {
    return this.connectionState === "connected";
  }

  public getIsDispenserActive(): boolean {
    return this.isDispenserActive;
  }

  /**
   * Start polling Dispenser status (/api/status)
   */
  public start(customUrl?: string) {
    if (typeof window === "undefined") return;

    if (customUrl) {
      this.esp32BaseUrl = this.normalizeUrl(customUrl);
    } else {
      try {
        const saved = localStorage.getItem("agribot_dispenser_url");
        if (saved && !saved.includes("192.168.8.108")) {
          this.esp32BaseUrl = this.normalizeUrl(saved);
        } else {
          this.esp32BaseUrl = "http://192.168.8.139";
          localStorage.setItem("agribot_dispenser_url", "http://192.168.8.139");
        }
      } catch {
        // Fallback
      }
    }

    this.checkStatus();

    if (!this.pollStatusTimer) {
      this.pollStatusTimer = setInterval(() => {
        this.checkStatus();
      }, 2000);
    }
  }

  public stop() {
    if (this.pollStatusTimer) {
      clearInterval(this.pollStatusTimer);
      this.pollStatusTimer = null;
    }
  }

  /**
   * Ping GET /api/status on Dispenser ESP32
   */
  public async checkStatus(): Promise<DispenserStatusResponse | null> {
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

      const data: DispenserStatusResponse = await res.json();
      this.isDispenserActive = !!data.dispenserActive;

      if (this.connectionState !== "connected") {
        this.connectionState = "connected";
        this.callbacks.onConnectionChange?.("connected", `Dispenser Online (${data.ip})`);
      }

      this.callbacks.onStatusUpdate?.(data);
      return data;
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : "Dispenser Offline";
      if (this.connectionState !== "disconnected") {
        this.connectionState = "disconnected";
        this.callbacks.onConnectionChange?.("disconnected", `Dispenser Offline (${errMsg})`);
      }
      return null;
    }
  }

  /**
   * Send START or STOP command to /api/command
   */
  public async sendCommand(cmd: "START" | "STOP" | "ON" | "OFF"): Promise<boolean> {
    try {
      this.isCommandInFlight = true;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

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
      if (res.ok) {
        if (cmd === "START" || cmd === "ON") {
          this.isDispenserActive = true;
        } else {
          this.isDispenserActive = false;
        }
        return true;
      }
      return false;
    } catch {
      this.isCommandInFlight = false;
      return false;
    }
  }

  public async turnOn(): Promise<boolean> {
    return await this.sendCommand("START");
  }

  public async turnOff(): Promise<boolean> {
    return await this.sendCommand("STOP");
  }
}

export const seedDispenserService = new SeedDispenserService();
export default seedDispenserService;
