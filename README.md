# Python Menu Backend

A no-dependency Python backend for your menu overlay system.

## Run

```bash
cd menu_backend_python
python3 server.py
```

It starts on:

```text
http://localhost:3000
```

## Endpoints

- `GET /health`
- `GET /screens`
- `GET /screens/:screenId/prices`
- `POST /screens/:screenId/prices`
- `PUT /screens/:screenId/prices`
- `DELETE /screens/:screenId/prices/:itemId`
- `GET /screens/:screenId/menu-state`
- `POST /screens/:screenId/menu-state`
