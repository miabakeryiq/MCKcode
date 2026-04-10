from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import os
from datetime import datetime

PORT = int(os.environ.get("PORT", "3000"))

# On Render free tier there is no persistent disk, so we store in /tmp
# which survives the process lifetime but resets on redeploy/spin-down.
# On a paid tier with a persistent disk mounted at /data, set:
#   DATA_DIR=/data
# via an environment variable in the Render dashboard.
DATA_DIR = os.environ.get("DATA_DIR", "/tmp/menu_data")
STORE_PATH = os.path.join(DATA_DIR, "store.json")

DEFAULT_STORE = {
    "screens": {
        "mckenzie-main": {
            "prices": {
                "beef_liver_s": 7,
                "beef_liver_m": 12,
                "beef_liver_l": 15,
                "ackee_saltfish_s": 11,
                "ackee_saltfish_m": 15,
                "ackee_saltfish_l": 18,
                "callaloo_saltfish_s": 7,
                "callaloo_saltfish_m": 12,
                "callaloo_saltfish_l": 15,
                "butterbeans_saltfish_s": 7,
                "butterbeans_saltfish_m": 12,
                "butterbeans_saltfish_l": 15,
                "cookup_saltfish_s": 7,
                "cookup_saltfish_m": 12,
                "cookup_saltfish_l": 15,
                "kidney_s": 7,
                "kidney_m": 12,
                "kidney_l": 15,
                "porridge_oatmeal_s": 5,
                "porridge_oatmeal_l": 8,
                "porridge_peanut_s": 5,
                "porridge_peanut_l": 8,
                "porridge_plantain_s": 5,
                "porridge_plantain_l": 8,
                "porridge_carrot_s": 5,
                "porridge_carrot_l": 8,
                "porridge_cornmeal_s": 5,
                "porridge_cornmeal_l": 8,
                "porridge_hominy_s": 5,
                "porridge_hominy_l": 8,
                "patty_curry_chicken": 3.5,
                "patty_beef_spicy": 3.5,
                "patty_beef_mild": 3.5,
                "patty_beefy_cheese": 3.5,
                "patty_veggie": 3.5,
                "patty_spinach": 4.0,
                "patty_spinach_cheese": 4.5,
                "patty_coco_bread": 1.5,
                "soup_chicken_s": 5,
                "soup_chicken_l": 8,
                "soup_beef_s": 5,
                "soup_beef_l": 8,
                "soup_red_peas_s": 5,
                "soup_red_peas_l": 8,
                "soup_goat_s": 10.0,
                "soup_goat_l": 8,
                "soup_cowfoot_s": 5,
                "soup_cowfoot_l": 8,
                "bev_dg_soda": 3.0,
                "bev_snapple": 2.5,
                "bev_tropical_rhythm": 2.5,
                "bev_canned_soda": 1.0,
                "bev_water": 1.0,
                "stew_chicken_s": 7,
                "stew_chicken_m": 15.0,
                "stew_chicken_l": 15
            },
            "meta": {
                "updatedAt": "2026-04-05T00:00:00.000Z",
                "source": "seed"
            }
        },
        "mckenzie-operate": {
            "prices": {
                "jerk_wings_s": 0,
                "jerk_wings_m": 0,
                "jerk_wings_l": 0,
                "stew_chicken_s": 0,
                "stew_chicken_m": 0,
                "stew_chicken_l": 0,
                "fried_chicken_s": 0,
                "fried_chicken_m": 0,
                "fried_chicken_l": 0,
                "escovitch_chicken_s": 0,
                "escovitch_chicken_m": 0,
                "escovitch_chicken_l": 0,
                "jerk_chicken_s": 0,
                "jerk_chicken_m": 0,
                "jerk_chicken_l": 0,
                "curry_chicken_s": 0,
                "curry_chicken_m": 0,
                "curry_chicken_l": 0,
                "stew_peas_s": 0,
                "stew_peas_m": 0,
                "stew_peas_l": 0,
                "escovitch_whiting_s": 0,
                "escovitch_whiting_m": 0,
                "escovitch_whiting_l": 0,
                "curry_goat_s": 0,
                "curry_goat_m": 0,
                "curry_goat_l": 0,
                "oxtail_s": 0,
                "oxtail_m": 0,
                "oxtail_l": 0,
                "salmon_s": 0,
                "salmon_m": 0,
                "salmon_l": 0,
                "glazed_salmon_s": 0,
                "glazed_salmon_m": 0,
                "glazed_salmon_l": 0,
                "snapper_s": 0,
                "snapper_m": 0,
                "snapper_l": 0,
                "chicken_jerk_quarter": 0,
                "chicken_jerk_half": 0,
                "chicken_fry_quarter": 0,
                "chicken_fry_half": 0,
                "chicken_wings_5pc": 0,
                "side_cabbage_s": 0,
                "side_cabbage_m": 0,
                "side_cabbage_l": 0,
                "side_white_rice_s": 0,
                "side_white_rice_m": 0,
                "side_white_rice_l": 0,
                "side_mac_cheese_s": 0,
                "side_mac_cheese_m": 0,
                "side_mac_cheese_l": 0,
                "side_festival_s": 0,
                "side_festival_m": 0,
                "side_festival_l": 0,
                "side_fried_plantain_s": 0,
                "side_fried_plantain_m": 0,
                "side_fried_plantain_l": 0,
                "side_fried_dumplings_s": 0,
                "side_fried_dumplings_m": 0,
                "side_fried_dumplings_l": 0,
                "side_pasta_s": 0,
                "side_pasta_m": 0,
                "side_pasta_l": 0
            },
            "meta": {
                "updatedAt": "2026-04-08T00:00:00.000Z",
                "source": "seed"
            }
        }
    }
}


def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
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
    def log_message(self, format, *args):
        # Cleaner logs on Render
        print(f"[{self.log_date_time_string()}] {format % args}")

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
    print(f"Data directory: {DATA_DIR}")
    print(f"Store path: {STORE_PATH}")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Python menu backend listening on http://0.0.0.0:{PORT}")
    server.serve_forever()
