from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import os
from datetime import datetime

PORT = int(os.environ.get("PORT", "3000"))
STORE_PATH = os.path.join(os.path.dirname(__file__), "data", "store.json")

DEFAULT_STORE = {
    "screens": {
        "mckenzie-main": {
            "prices": {
                "beef_liver_s": 7,
                "beef_liver_m": 12,
                "beef_liver_l": 15,
                "ackee_saltfish_s": 11,
                "ackee_saltfish_m": 15,
                "ackee_saltfish_l": 18
            },
            "meta": {
                "updatedAt": "2026-04-04T00:00:00.000Z",
                "source": "seed"
            }
        }
    }
}


def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ensure_store():
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    if not os.path.exists(STORE_PATH):
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_STORE, f, indent=2)


def read_store():
    ensure_store()
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_store(store):
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)


def clean_prices(payload):
    if not isinstance(payload, dict):
        raise ValueError("Body must be a JSON object")
    out = {}
    for key, value in payload.items():
        try:
            out[key] = round(float(value), 2)
        except Exception:
            raise ValueError(f'Invalid price for "{key}"')
    return out


def get_or_create_screen(store, screen_id):
    if screen_id not in store["screens"]:
        store["screens"][screen_id] = {
            "prices": {},
            "meta": {"updatedAt": now_iso(), "source": "created"}
        }
    return store["screens"][screen_id]


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            raise ValueError("Invalid JSON body")

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        store = read_store()
        path = urlparse(self.path).path
        parts = [p for p in path.split("/") if p]

        if path == "/health":
            return self._send_json(200, {"ok": True, "service": "menu-overlay-backend-python", "time": now_iso()})

        if path == "/screens":
            screens = []
            for screen_id, value in store["screens"].items():
                screens.append({
                    "screenId": screen_id,
                    "itemCount": len(value.get("prices", {})),
                    "updatedAt": value.get("meta", {}).get("updatedAt")
                })
            return self._send_json(200, {"screens": screens})

        if len(parts) == 3 and parts[0] == "screens" and parts[2] == "prices":
            screen_id = parts[1]
            screen = store["screens"].get(screen_id)
            if not screen:
                return self._send_json(404, {"error": "Screen not found"})
            return self._send_json(200, screen.get("prices", {}))

        if len(parts) == 3 and parts[0] == "screens" and parts[2] == "menu-state":
            screen_id = parts[1]
            screen = store["screens"].get(screen_id)
            if not screen:
                return self._send_json(404, {"error": "Screen not found"})
            return self._send_json(200, {
                "screenId": screen_id,
                "prices": screen.get("prices", {}),
                "soldOut": screen.get("soldOut", []),
                "labels": screen.get("labels", {}),
                "meta": screen.get("meta", {})
            })

        return self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        try:
            store = read_store()
            path = urlparse(self.path).path
            parts = [p for p in path.split("/") if p]

            if len(parts) == 3 and parts[0] == "screens" and parts[2] == "prices":
                screen_id = parts[1]
                payload = self._read_json_body()
                updates = clean_prices(payload)
                screen = get_or_create_screen(store, screen_id)
                screen["prices"] = {**screen.get("prices", {}), **updates}
                screen["meta"] = {**screen.get("meta", {}), "updatedAt": now_iso(), "source": "merge"}
                write_store(store)
                return self._send_json(200, {
                    "ok": True,
                    "screenId": screen_id,
                    "mode": "merge",
                    "updatedKeys": list(updates.keys()),
                    "prices": screen["prices"],
                    "meta": screen["meta"]
                })

            if len(parts) == 3 and parts[0] == "screens" and parts[2] == "menu-state":
                screen_id = parts[1]
                payload = self._read_json_body()
                screen = get_or_create_screen(store, screen_id)

                if "prices" in payload:
                    screen["prices"] = {**screen.get("prices", {}), **clean_prices(payload["prices"])}
                if "soldOut" in payload:
                    if not isinstance(payload["soldOut"], list):
                        raise ValueError("soldOut must be an array")
                    screen["soldOut"] = payload["soldOut"]
                if "labels" in payload:
                    if not isinstance(payload["labels"], dict):
                        raise ValueError("labels must be an object")
                    screen["labels"] = payload["labels"]

                screen["meta"] = {**screen.get("meta", {}), "updatedAt": now_iso(), "source": "menu-state"}
                write_store(store)
                return self._send_json(200, {
                    "ok": True,
                    "screenId": screen_id,
                    "menuState": {
                        "prices": screen.get("prices", {}),
                        "soldOut": screen.get("soldOut", []),
                        "labels": screen.get("labels", {}),
                        "meta": screen.get("meta", {})
                    }
                })

            return self._send_json(404, {"error": "Not found"})
        except ValueError as e:
            return self._send_json(400, {"error": str(e)})
        except Exception as e:
            return self._send_json(500, {"error": str(e)})

    def do_PUT(self):
        try:
            store = read_store()
            path = urlparse(self.path).path
            parts = [p for p in path.split("/") if p]

            if len(parts) == 3 and parts[0] == "screens" and parts[2] == "prices":
                screen_id = parts[1]
                payload = self._read_json_body()
                prices = clean_prices(payload)
                screen = get_or_create_screen(store, screen_id)
                screen["prices"] = prices
                screen["meta"] = {**screen.get("meta", {}), "updatedAt": now_iso(), "source": "replace"}
                write_store(store)
                return self._send_json(200, {
                    "ok": True,
                    "screenId": screen_id,
                    "mode": "replace",
                    "prices": screen["prices"],
                    "meta": screen["meta"]
                })

            return self._send_json(404, {"error": "Not found"})
        except ValueError as e:
            return self._send_json(400, {"error": str(e)})
        except Exception as e:
            return self._send_json(500, {"error": str(e)})

    def do_DELETE(self):
        try:
            store = read_store()
            path = urlparse(self.path).path
            parts = [p for p in path.split("/") if p]

            if len(parts) == 4 and parts[0] == "screens" and parts[2] == "prices":
                screen_id = parts[1]
                item_id = parts[3]
                screen = store["screens"].get(screen_id)
                if not screen:
                    return self._send_json(404, {"error": "Screen not found"})
                screen.get("prices", {}).pop(item_id, None)
                screen["meta"] = {**screen.get("meta", {}), "updatedAt": now_iso(), "source": "delete"}
                write_store(store)
                return self._send_json(200, {
                    "ok": True,
                    "screenId": screen_id,
                    "removed": item_id,
                    "prices": screen.get("prices", {})
                })

            return self._send_json(404, {"error": "Not found"})
        except Exception as e:
            return self._send_json(500, {"error": str(e)})


if __name__ == "__main__":
    ensure_store()
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Python menu backend listening on http://localhost:{PORT}")
    server.serve_forever()
