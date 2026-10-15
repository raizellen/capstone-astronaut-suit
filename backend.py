import argparse
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

METRICS = ["bpm", "spo2", "battery", "temperature"]

# expected ranges, for warnings only
EXPECTED = {
  "bpm": (20, 250, "bpm"),
  "spo2": (50, 100, "%"),
  "battery": (0, 100, "%"),
  "temperature": (-100, 100, "deg C"),
}

# latest known value per metric
current = {"bpm": 75, "spo2": 98, "battery": 90, "temperature": 21}

class Handler(BaseHTTPRequestHandler):
  def log_message(self, format, *args):
    pass

  def _send(self, code, obj):
    payload = json.dumps(obj).encode()
    self.send_response(code)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(payload)))
    self.end_headers()
    self.wfile.write(payload)

  def do_GET(self):
    # for checking the server is reachable from browser
    if self.path == "/telemetry":
      self._send(200, current)
    else:
      self._send(404, {"ok": False, "error": "Not found"})

  def do_POST(self):
    if self.path != "/telemetry":
      self._send(404, {"ok": False, "error": "Not found"})
      return

    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length)

    try:
      update = json.loads(body)
    except json.JSONDecodeError:
      self._send(400, {"ok": False, "error": "Invalid JSON body"})
      return

    if not isinstance(update, dict):
      self._send(400, {"ok": False, "error": "Body must be a JSON object"})
      return

    warnings = []
    for metric, value in update.items():
        if metric not in METRICS:
          warnings.append(f"unknown field '{metric}' (ignored)")
          continue

        if isinstance(value, bool) or not isinstance(value, (int, float)):
          warnings.append(
            f"{metric}: expected a number, got {type(value).__name__} (ignored)"
          )
          continue

        lo, hi, unit = EXPECTED[metric]
        if not lo <= value <= hi:
          warnings.append(
            f"{metric}={value} is outside the expected range {lo} to {hi} {unit}"
          )

        current[metric] = value

    stamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{stamp}] received {update}", flush=True)
    for w in warnings:
      print(f"           warning: {w}", flush=True)

    self._send(200, {"ok": True, "telemetry": current, "warnings": warnings})


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--port", type=int, default=8080)
  args = parser.parse_args()

  server = HTTPServer(("0.0.0.0", args.port), Handler)
  print(f"backend listening on port {args.port}")
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    print("\nStopped.")


if __name__ == "__main__":
  main()