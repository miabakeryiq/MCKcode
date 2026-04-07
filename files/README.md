# Python Menu Backend

A no-dependency Python backend for the MCK menu overlay system.

---

## Deploy to Render

### Step 1 — Push these files to your repo
Make sure your `master` branch contains:
```
server.py
requirements.txt
render.yaml        ← optional but recommended
```

### Step 2 — Create a new Web Service on Render
Go to https://dashboard.render.com and click **New → Web Service**.

| Field | Value |
|---|---|
| **Repository** | `miabakeryiq / MCKcode` |
| **Branch** | `master` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python server.py` |
| **Instance Type** | Free (or paid for persistence) |

### Step 3 — Environment variables
No required variables on the free tier. Render automatically sets `PORT`.

Optional (paid tier with disk only):
| Key | Value |
|---|---|
| `DATA_DIR` | `/data` |

### Step 4 — Deploy
Click **Deploy Web Service**. Once live, your base URL will be:
```
https://<your-service-name>.onrender.com
```

---

## ⚠️ Free Tier — Data Persistence Warning

On Render's **free tier**, the service spins down after inactivity and restarts
with a fresh filesystem. Price updates you POST/PUT will be **lost on restart**.

The server falls back to the seed data in `DEFAULT_STORE` (inside `server.py`)
on every cold start.

**To make data persist**, upgrade to a paid instance and add a Render Disk:
- Mount path: `/data`
- Set env var `DATA_DIR=/data`
- Uncomment the `disk` block in `render.yaml`

---

## Run Locally

```bash
python server.py
# Listening on http://localhost:3000
```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/screens` | List all screens |
| GET | `/screens/:screenId/prices` | Get prices for a screen |
| POST | `/screens/:screenId/prices` | Merge prices |
| PUT | `/screens/:screenId/prices` | Replace all prices |
| DELETE | `/screens/:screenId/prices/:itemId` | Remove one price |
| GET | `/screens/:screenId/menu-state` | Full menu state |
| POST | `/screens/:screenId/menu-state` | Update full menu state |

---

## Quick Test (after deploy)

Replace `BASE` with your Render URL or `http://localhost:3000`.

```bash
BASE=https://<your-service>.onrender.com

# Health check
curl $BASE/health

# Get prices
curl $BASE/screens/mckenzie-main/prices

# Merge a price update
curl -X POST $BASE/screens/mckenzie-main/prices \
  -H "Content-Type: application/json" \
  -d '{"beef_liver_s": 9}'

# Replace all prices
curl -X PUT $BASE/screens/mckenzie-main/prices \
  -H "Content-Type: application/json" \
  -d '{"beef_liver_s": 8, "beef_liver_m": 13}'
```
