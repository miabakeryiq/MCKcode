# Menu backend integration kit

Files in this folder:

- `overlay-player-api.html`  
  Player version that polls the backend for prices.
- `menu-middleware-app.html`  
  A middleware app that edits and pushes prices to the backend.
- `backend-quickstart.md`  
  Fast setup notes.

## Local loop

<!-- 1. Run the backend:
   ```bash
   cd menu_backend
   npm install
   npm run dev
   ``` -->

2. Open the player and point it at:
   `http://localhost:3000/screens/mckenzie-main/prices`

3. Run the middleware app in your React environment and set:
   - API base: `http://localhost:3000`
   - Screen ID: `mckenzie-main`

4. Edit a price and push it.
5. The player polls every 5 seconds and updates.

## Notes

- Keep `overlay-map.json`, HTML, and media hosted as static files.
- Keep live prices in the backend.
- This middleware app uses the overlay item ids directly so the backend and player stay aligned.
