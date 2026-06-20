import { useEffect, useState } from "react";

const WS_BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace("http", "ws");

/**
 * Subscribes to real-time outbreak alerts for the user's local area
 * (identified by a geohash prefix, never an exact address) and shows the
 * most severe active alert as a dismissible banner.
 */
export default function AlertBanner() {
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    const geohashPrefix = localStorage.getItem("home_geohash_prefix") || "dr5r"; // fallback demo cell
    const ws = new WebSocket(`${WS_BASE}/alerts/ws/${geohashPrefix}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setAlert(data);
    };

    const keepalive = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);

    return () => {
      clearInterval(keepalive);
      ws.close();
    };
  }, []);

  if (!alert) return null;

  return (
    <div className={`alert-banner alert-banner--${alert.severity_level}`} role="alert">
      <strong>{alert.severity_level.toUpperCase()}:</strong> {alert.message}
      <button onClick={() => setAlert(null)} aria-label="Dismiss alert">×</button>
    </div>
  );
}
