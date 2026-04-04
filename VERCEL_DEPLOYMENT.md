# Vercel Deployment

## What this setup does

This repo now supports serving the protected map directly from Vercel:

- `/login` is handled by a Vercel serverless function that serves the login page
- `/api/login` validates the shared password and sets an HTTP-only session cookie
- `/` and `/index.html` are rewritten to a protected Vercel function that injects `GOOGLE_MAPS_API_KEY` at request time
- `/logout` clears the session cookie

## Required environment variables

Set these in the Vercel project:

- `GOOGLE_MAPS_API_KEY`
- `MAP_LOGIN_PASSWORD`
- `SESSION_SECRET`

Notes:

- `MAP_LOGIN_PASSWORD` is the shared password for the site
- `SESSION_SECRET` should be a long random string

## Local run

The Vercel frontend routes are included in the repo, but the easiest local smoke test is still the Express server:

```powershell
npm install
npm start
```

Then open:

```text
http://localhost:3000/login
```

## Vercel deploy

1. Push this repo to GitHub.
2. Import the repo into Vercel.
3. Add the required environment variables.
4. Deploy.

Vercel uses the included `vercel.json` rewrites to route `/`, `/login`, `/logout`, and `/health`.

## Current limitation

The Vercel session cookie is signed and expires after 12 hours, but it is still a simple shared-password gate.

If you later want per-user accounts, audit logs, or revocable sessions, we should move auth to a dedicated identity provider or backend store.
