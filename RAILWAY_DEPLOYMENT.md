# Railway Deployment

## What this setup does

This project now runs through a small Node.js server that:

- shows a password login page at `/login`
- creates an authenticated session cookie after successful sign-in
- serves the existing root `index.html` only to signed-in users
- injects `GOOGLE_MAPS_API_KEY` into the page at request time so the browser key is not hardcoded into the committed HTML

The map itself is still the generated single-file interface.

## Required environment variables

Set these in Railway:

- `GOOGLE_MAPS_API_KEY`
- `MAP_LOGIN_PASSWORD`
- `SESSION_SECRET`

Notes:

- `MAP_LOGIN_PASSWORD` is the shared password for the site
- `SESSION_SECRET` should be a long random string

## Local run

Install dependencies:

```powershell
npm install
```

Start the app:

```powershell
npm start
```

Before local start, make sure `.env` contains:

```text
GOOGLE_MAPS_API_KEY=...
MAP_LOGIN_PASSWORD=...
SESSION_SECRET=...
```

Open:

```text
http://localhost:3000/login
```

## Railway deploy

1. Push this repo to GitHub.
2. Create a new Railway project from the GitHub repo.
3. Add the required environment variables in Railway.
4. Deploy.

Railway will start the app with:

```text
npm start
```

The built-in health check path is:

```text
/health
```

## Current limitation

This first pass uses the default in-memory session store from `express-session`.

That is fine for a simple private deployment, but if you later run multiple instances or want persistent session storage across restarts, we should move sessions to Redis or another shared store.
