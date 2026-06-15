type MessageHandler = (data: any) => void;

export class WebSocketClient {
  private url: string;
  private ws: WebSocket | null = null;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(endpoint: string) {
    const token = typeof window !== "undefined" ? localStorage.getItem("airlynk_access_token") : null;
    const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    this.url = `${baseUrl}${endpoint}${token ? `?token=${token}` : ""}`;
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.ws = new WebSocket(this.url);

    this.ws.onmessage = (event) => {
      try {
        if (event.data === "pong") return;
        const data = JSON.parse(event.data);
        this.handlers.forEach(handler => handler(data));
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000));
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    // Keepalive ping
    const pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send("ping");
      } else {
        clearInterval(pingInterval);
      }
    }, 30000);
  }

  subscribe(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
