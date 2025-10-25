## Sprint 04 — Playlists & Selection UI (short)

### Goals
- Add a simple practice type selector and Next item control
- Introduce session‑scoped playlists (by item IDs)
- Expose long_alt descriptions for media (accessibility)

### Scope delivered
- Backend
  - Selection: playlist support with preserved order; no implicit type narrowing when a playlist is active; no shuffle under playlist; simple policy rotation disabled under playlist
  - Endpoints: `GET /api/item/types`, `GET /api/item/ids?type=...`, `POST /api/playlist`, `DELETE /api/playlist`
  - Readiness: includes canonical item count and types
- Frontend
  - Type dropdown + Next item button; fetches `/api/item/next?type=...`
  - Playlist Apply/Clear (comma‑separated IDs); Next respects playlist
  - Auto‑advance to next item on correct final step; multi‑step stays within steps first
  - `long_alt` affordance for item and choice media via expandable details
- Docs & Data
  - `docs/API_CONTRACT.md`: documented new endpoints
  - Added `data/canonical/i_type_a_003.json`, `_b_003.json`, `_c_003.json` (with long_alt media)

### Acceptance results
- Type selector lists server‑seen types; Next fetches only the selected type
- With a playlist, items cycle in provided order across types; no immediate repeats unless playlist size is 1
- Progress reflects attempts/correct by type; endpoints return expected payloads

### How to test (local)
1) Start backend (file mode) and frontend
2) Visit FE → verify type selector and Next
3) Set a playlist (e.g., `i_type_a_001,i_type_a_003,i_type_b_001`) → Apply → click Next to cycle
4) Expand “More description” on media where `long_alt` is present
5) Optional endpoints:
   - `GET /api/item/types`
   - `GET /api/item/ids?type=TYPE_A`
   - `GET /api/readiness` (check canonical.types)

### Out of scope / Follow‑ups
- Persist last selected type/playlist across reloads
- FE ID picker fed by `/api/item/ids`
- Auth/onboarding & roles

