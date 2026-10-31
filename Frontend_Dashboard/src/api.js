const API = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

async function read(path) {
  const response = await fetch(`${API}${path}`);
  if (!response.ok) {
    throw new Error(`API ${response.status}`);
  }
  return response.json();
}

export function getLatest() {
  return read("/api/latest");
}

export function getHistory() {
  return read("/api/history?limit=40");
}

export function getAlerts() {
  return read("/api/alerts");
}

export async function sendCommand(command) {
  const response = await fetch(`${API}/api/commands`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(command),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || `API ${response.status}`);
  }
  return body;
}
