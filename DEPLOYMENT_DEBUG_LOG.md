# Deployment And Debug Log

## Current deployment shape

- GitHub repo: `https://github.com/heund/shrines_map`
- Current production target: Railway
- App entrypoint: `server.js`
- Start command: `npm start`
- Default local port: `3000`
- Production port: `process.env.PORT`

## What we changed

### App protection and environment handling

- Added a shared-password login flow at `/login`
- Replaced the original open static page flow with a protected server-rendered response
- Injected `GOOGLE_MAPS_API_KEY` into `index.html` at request time instead of relying on a committed hardcoded key
- Standardized auth around signed cookies

### Deployment support

- Configured the app for Railway-compatible startup using `process.env.PORT`
- Added `/health`
- Confirmed the required Railway environment variables are:
  - `GOOGLE_MAPS_API_KEY`
  - `MAP_LOGIN_PASSWORD`
  - `SESSION_SECRET`

### Map interface updates

- Renamed venue-facing UI from `비엔날레 장소` to `비엔날레 베뉴`
- Updated the main title to `제5회 제주비엔날레 QR코드 매핑 전략 자료`
- Added top quick-filter buttons for:
  - `지도 랜드마크`
  - `비엔날레 베뉴`
  - `신당`
  - `문화유산`
- Reordered sidebar controls so `기본 지도` appears first
- Removed the `지형` and `위성` custom basemap options, leaving `기본` and `하이브리드`
- Moved `원도심 포커스` to the left-bottom corner so it no longer blocks Street View
- Fixed the venue click behavior so clicking a venue opens its own marker instead of causing the layer state to flicker

### Venue route / `동선 표시`

- Added `동선 표시` as a button instead of a checkbox
- Changed it to be off by default on initial load
- Switched the route overlay from live API-based routing to a local curated route file:
  - `locations/venue-route.json`
- Added an authenticated Railway route so the frontend can fetch:
  - `/locations/venue-route.json`

## Errors we encountered

### 1. Railway login succeeded but the map page did not appear correctly

Symptoms:

- Railway kept returning the login page
- Successful login did not reliably reach the protected map

What we found:

- The original session handling path was not behaving reliably in the deployed environment

What we changed:

- Simplified the auth flow around signed cookies shared across the deployment paths

### 2. Google Maps key injection failed on Railway

Error:

```text
Failed to inject GOOGLE_MAPS_API_KEY into index.html
```

What we found:

- The HTML injection code treated an unchanged replacement result as failure
- If the env var value matched the already-present key pattern, the result could be unchanged even though the replacement target was valid

What we changed:

- Updated the key injection logic to validate the target pattern itself rather than assuming unchanged output meant failure

### 3. Railway served the map HTML but `동선 표시` failed with Google routing errors

Errors:

```text
Directions request returned no results.
Failed to build venue leg ... no drivable segment was found.
Failed to build venue route: no road-connected segments found.
```

What we tried first:

- Google Directions API
- Google Roads API `nearestRoads`
- Multiple nearby access-point candidates around each venue
- Driving-first plus walking fallback logic

What we found:

- The problem was not just our routing code
- Google Maps Platform routing support for Korea was the blocker for this use case
- Even obviously road-connected venue pairs kept failing through Google’s routing services

Decision:

- Do not depend on Google live routing for `동선 표시`
- Keep Google only as the basemap
- Store and draw the route locally

### 4. After moving to a local route file, Railway returned `404` for the route JSON

Error:

```text
/locations/venue-route.json 404
```

What we found:

- The frontend was requesting the JSON correctly
- The file existed in the repo
- But the Express app did not expose a route for that path

What we changed:

- Added a protected Express route in `server.js` for:
  - `/locations/venue-route.json`

## How we debugged things

### Deployment debugging approach

1. Read the exact runtime error from Railway or browser console first
2. Trace whether the failure was:
   - frontend-only
   - server-only
   - environment/configuration-only
3. Confirm whether the issue came from:
   - missing env vars
   - auth/session behavior
   - static asset serving
   - third-party API limitations
4. Replace fragile runtime dependencies with local deterministic data when provider behavior was the real blocker

### Route debugging approach

1. Confirm the failing venue legs from console warnings
2. Test whether the problem was raw venue coordinates or road-access coordinates
3. Expand the search to nearby access candidates
4. Add walking fallback
5. Re-evaluate the provider instead of endlessly tuning the same failing API path
6. Replace live routing with curated route geometry once the provider limitation was clear

## Files most relevant to the current setup

- `server.js`
- `index.html`
- `lib/render-index-html.js`
- `lib/session-auth.js`
- `locations/venues.json`
- `locations/venue-route.json`
- `RAILWAY_DEPLOYMENT.md`

## Current known limitations

- `동선 표시` is now a curated local route, not a live navigation result
- If the red path needs refinement, edit `locations/venue-route.json`
- Auth is still a shared-password gate, not a user account system

## Recommended next steps

1. Redeploy Railway from the latest `master`
2. Verify:
   - `/login`
   - `/health`
   - protected map load after login
   - `동선 표시` button loads the red route without console errors
3. If the route shape needs improvement, refine the coordinates in `locations/venue-route.json`
