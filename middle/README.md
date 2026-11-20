# Middle Screen

The Middle Screen is a full player/editor pair built from the same pattern as `player/` and `operate/`.

- `index.html` — live player; plays `middle_screen.mp4`, overlays prices, polls the `mckenzie-middle` backend screen every 5 seconds.
- `overlay-editor-middle.html` — drag/nudge editor for the Middle Screen overlay coordinates.
- `overlay-map-middle.json` — Middle Screen price coordinates.
- `prices.json` — local fallback/default prices. The source video visibly shows `$17.00` for Jerk Wings + Mac (L); the other video prices are not visibly supplied, so they remain `0` until set in middleware/backend.
- `middle_screen.mp4` — source video.
- `middle_screen.png` — first-frame editor preview.
