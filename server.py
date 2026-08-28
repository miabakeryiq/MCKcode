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
STORE_PATH       = os.path.join(DATA_DIR, "store.json")
TOAST_QUEUE_PATH  = os.path.join(DATA_DIR, "toast_queue.json")
OVERLAY_MAPS_DIR  = os.path.join(DATA_DIR, "overlay_maps")
TOAST_SECRET     = os.environ.get("TOAST_WEBHOOK_SECRET", "changeme")

DEFAULT_STORE = {
    "screens": {
        "mckenzie-main": {
            "prices": {
                "beef_liver_s": 7,
                "beef_liver_m": 12,
                "beef_liver_l": 15,
                "stew_chicken_s": 7,
                "stew_chicken_m": 15,
                "stew_chicken_l": 15,
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
                "soup_goat_s": 10,
                "soup_goat_l": 8,
                "soup_cowfoot_s": 5,
                "soup_cowfoot_l": 8,
                "bev_dg_soda": 3.0,
                "bev_squeezr": 2.5,
                "bev_tru_juice": 2.5,
                "bev_canned_soda": 1.0,
                "bev_water": 1.0
            },
            "meta": {"updatedAt": "2026-04-05T00:00:00.000Z", "source": "seed"}
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
                "glazed_salmon_s": 0,
                "glazed_salmon_m": 0,
                "glazed_salmon_l": 0,
                "snapper_l": 0,
                "jerk_pork_s": 0,
                "jerk_pork_m": 0,
                "jerk_pork_l": 0,
                "chicken_jerk_quarter": 0,
                "chicken_jerk_half": 0,
                "chicken_fry_quarter": 0,
                "chicken_fry_half": 0,
                "chicken_wings_5pc": 0,
                "side_rice_peas_s": 0,
                "side_rice_peas_m": 0,
                "side_rice_peas_l": 0,
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
            "meta": {"updatedAt": "2026-04-08T00:00:00.000Z", "source": "seed"}
        },
        "mckenzie-middle": {
            "prices": {
                "middle_curry_chicken_roti": 0,
                "middle_goat_roti": 0,
                "middle_oxtail_roti": 0,
                "middle_jerk_chicken_roti": 0,
                "middle_vegetable_roti": 0,
                "middle_roti_skin": 0,
                "middle_jerk_chicken_mac_s": 0,
                "middle_jerk_chicken_mac_m": 0,
                "middle_jerk_chicken_mac_l": 0,
                "middle_stew_chicken_mac_s": 0,
                "middle_stew_chicken_mac_m": 0,
                "middle_stew_chicken_mac_l": 0,
                "middle_curry_chicken_mac_s": 0,
                "middle_curry_chicken_mac_m": 0,
                "middle_curry_chicken_mac_l": 0,
                "middle_fried_chicken_mac_s": 0,
                "middle_fried_chicken_mac_m": 0,
                "middle_fried_chicken_mac_l": 0,
                "middle_curry_goat_mac_s": 0,
                "middle_curry_goat_mac_m": 0,
                "middle_curry_goat_mac_l": 0,
                "middle_jerk_pork_mac_s": 0,
                "middle_jerk_pork_mac_m": 0,
                "middle_jerk_pork_mac_l": 0,
                "middle_barby_fried_mac_s": 0,
                "middle_barby_fried_mac_m": 0,
                "middle_barby_fried_mac_l": 0,
                "middle_oxtail_mac_s": 0,
                "middle_oxtail_mac_m": 0,
                "middle_oxtail_mac_l": 0,
                "middle_whiting_mac_s": 0,
                "middle_whiting_mac_m": 0,
                "middle_whiting_mac_l": 0,
                "middle_shrimps_mac_s": 0,
                "middle_shrimps_mac_m": 0,
                "middle_shrimps_mac_l": 0,
                "middle_jerk_wings_mac_s": 0,
                "middle_jerk_wings_mac_m": 0,
                "middle_jerk_wings_mac_l": 0,
                "middle_salmon_mac_s": 0,
                "middle_salmon_mac_m": 0,
                "middle_salmon_mac_l": 0,
                "middle_jerk_chicken_pasta": 0,
                "middle_stew_chicken_pasta": 0,
                "middle_curry_chicken_pasta": 0,
                "middle_fried_chicken_pasta": 0,
                "middle_curry_goat_pasta": 0,
                "middle_shrimp_pasta": 0,
                "middle_jerk_pork_pasta": 0,
                "middle_glazed_salmon_pasta": 0,
                "middle_oxtail_pasta": 0,
                "middle_snapper_pasta": 0
            },
            "meta": {"updatedAt": "2026-04-08T00:00:00.000Z", "source": "seed"}
        }
    }
}


def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ensure_store():
    """Create the store if needed and migrate newly-added screens into an existing store."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(STORE_PATH):
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_STORE, f, indent=2)
        return

    # Existing Render data survives while the process is running.  When Screen 3
    # is added to the codebase, an existing store.json will NOT be recreated, so
    # explicitly migrate the new screen into it.
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            store = json.load(f)
    except Exception:
        # Let read_store surface a useful error rather than silently replacing data.
        return

    changed = False
    for screen_id, default_screen in DEFAULT_STORE.get("screens", {}).items():
        if screen_id not in store.setdefault("screens", {}):
            store["screens"][screen_id] = default_screen
            changed = True

    if changed:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)


def read_store():
    ensure_store()
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_store(store):
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)



def read_toast_queue() -> list:
    if not os.path.exists(TOAST_QUEUE_PATH):
        return []
    with open(TOAST_QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_toast_queue(queue: list):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TOAST_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)



def overlay_map_path(screen_id: str) -> str:
    return os.path.join(OVERLAY_MAPS_DIR, f"{screen_id}.json")

def read_overlay_map(screen_id: str) -> dict:
    path = overlay_map_path(screen_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_overlay_map(screen_id: str, data: dict):
    os.makedirs(OVERLAY_MAPS_DIR, exist_ok=True)
    with open(overlay_map_path(screen_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


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

        # Overlay map — GET /overlay-map/:screenId
        if len(parts) == 2 and parts[0] == "overlay-map":
            screen_id = parts[1]
            data = read_overlay_map(screen_id)
            if data is None:
                return self._send_json(404, {"error": "Overlay map not found. Upload via POST first."})
            return self._send_json(200, data)

        # Toast webhook — fetch pending updates
        if path == "/webhook/toast/pending":
            secret = self.headers.get("X-Toast-Secret", "")
            if secret != TOAST_SECRET:
                return self._send_json(403, {"error": "Forbidden"})
            return self._send_json(200, {"updates": read_toast_queue()})

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

            # Overlay map — POST /overlay-map/:screenId (upload full map)
            if len(parts) == 2 and parts[0] == "overlay-map":
                screen_id = parts[1]
                payload = self._read_json_body()
                if not isinstance(payload.get("items"), list):
                    raise ValueError("Invalid overlay map — must have items array")
                write_overlay_map(screen_id, payload)
                return self._send_json(200, {"ok": True, "screenId": screen_id, "itemCount": len(payload["items"])})

            # Overlay map — PATCH /overlay-map/:screenId/item/:itemId (update single item label)
            if len(parts) == 4 and parts[0] == "overlay-map" and parts[2] == "item":
                screen_id = parts[1]
                item_id   = parts[3]
                payload   = self._read_json_body()
                data = read_overlay_map(screen_id)
                if data is None:
                    return self._send_json(404, {"error": "Overlay map not found"})
                updated = False
                for item in data.get("items", []):
                    if item["id"] == item_id:
                        if "label" in payload:
                            item["label"] = str(payload["label"])
                        updated = True
                        break
                if not updated:
                    return self._send_json(404, {"error": f"Item {item_id!r} not found in map"})
                write_overlay_map(screen_id, data)
                return self._send_json(200, {"ok": True, "screenId": screen_id, "itemId": item_id})

            # Toast webhook — receive price update from Toast bot
            if path == "/webhook/toast":
                secret = self.headers.get("X-Toast-Secret", "")
                if secret != TOAST_SECRET:
                    return self._send_json(403, {"error": "Forbidden"})
                payload = self._read_json_body()
                items = payload.get("items", [])
                if not isinstance(items, list):
                    raise ValueError("items must be an array")
                queue = read_toast_queue()
                import uuid
                for item in items:
                    queue.append({
                        "id":    str(uuid.uuid4()),
                        "name":  item.get("name", ""),
                        "price": float(item.get("price", 0)),
                        "receivedAt": now_iso()
                    })
                write_toast_queue(queue)
                # Also immediately update McKenzie screen prices
                screen = get_or_create_screen(store, "mckenzie-main")
                # Note: name→id mapping lives in OmniSync config.py, not here.
                # Raw Toast items are queued; OmniSync resolves IDs and pushes platforms.
                return self._send_json(200, {"ok": True, "queued": len(items)})

            # Toast webhook — acknowledge processed updates (remove from queue)
            if path == "/webhook/toast/ack":
                secret = self.headers.get("X-Toast-Secret", "")
                if secret != TOAST_SECRET:
                    return self._send_json(403, {"error": "Forbidden"})
                payload = self._read_json_body()
                ack_ids = set(payload.get("ids", []))
                queue = read_toast_queue()
                remaining = [u for u in queue if u.get("id") not in ack_ids]
                write_toast_queue(remaining)
                return self._send_json(200, {"ok": True, "removed": len(queue) - len(remaining)})

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
