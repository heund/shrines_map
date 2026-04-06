const path = require("path");

const dotenv = require("dotenv");
const express = require("express");

const { renderIndexHtml } = require("./lib/render-index-html");
const {
  buildClearSessionCookie,
  buildSessionCookie,
  createSessionToken,
  readSession
} = require("./lib/session-auth");

dotenv.config();

const app = express();
const PORT = Number(process.env.PORT || 3000);
const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const MAP_PASSWORD = process.env.MAP_LOGIN_PASSWORD;
const SESSION_SECRET = process.env.SESSION_SECRET;
const LOGIN_PATH = path.join(__dirname, "public", "login.html");
const VENUE_ROUTE_PATH = path.join(__dirname, "locations", "venue-route.json");
const SHRINE_IMAGES_PATH = path.join(__dirname, "shrine", "images");

if (!GOOGLE_MAPS_API_KEY) {
  throw new Error("Missing required environment variable: GOOGLE_MAPS_API_KEY");
}

if (!MAP_PASSWORD) {
  throw new Error("Missing required environment variable: MAP_LOGIN_PASSWORD");
}

if (!SESSION_SECRET) {
  throw new Error("Missing required environment variable: SESSION_SECRET");
}

app.disable("x-powered-by");
app.set("trust proxy", 1);

app.use((req, res, next) => {
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  next();
});

app.use(express.urlencoded({ extended: false }));

async function isAuthenticated(req) {
  return Boolean(await readSession(req));
}

async function requireAuth(req, res, next) {
  if (await isAuthenticated(req)) {
    return next();
  }
  return res.redirect("/login");
}

function setNoStore(res) {
  res.setHeader("Cache-Control", "no-store");
}

function handleHealth(_req, res) {
  res.json({ ok: true });
}

async function handleLoginPage(req, res) {
  if (await isAuthenticated(req)) {
    return res.redirect("/");
  }

  setNoStore(res);
  return res.sendFile(LOGIN_PATH);
}

async function handleLogin(req, res) {
  const password = String(req.body.password || "");

  if (password !== MAP_PASSWORD) {
    return res.redirect("/login?error=1");
  }

  const token = await createSessionToken();
  res.setHeader("Set-Cookie", buildSessionCookie(token));
  return res.redirect("/");
}

function handleLogout(req, res) {
  res.setHeader("Set-Cookie", buildClearSessionCookie());
  return res.redirect("/login");
}

function handleMap(_req, res) {
  setNoStore(res);
  res.type("html").send(renderIndexHtml(GOOGLE_MAPS_API_KEY));
}

function handleVenueRoute(_req, res) {
  setNoStore(res);
  return res.sendFile(VENUE_ROUTE_PATH);
}

function handleShrineImage(req, res) {
  setNoStore(res);

  const imageName = String(req.params.imageName || "");
  if (!/^[A-Za-z0-9_-]+\.(png|jpg|jpeg|webp)$/i.test(imageName)) {
    return res.status(404).send("Not found");
  }

  return res.sendFile(imageName, { root: SHRINE_IMAGES_PATH }, (error) => {
    if (error && !res.headersSent) {
      res.status(error.statusCode || 404).send("Not found");
    }
  });
}

app.get("/health", handleHealth);

app.get("/favicon.ico", (_req, res) => {
  res.status(204).end();
});

app.get("/login", handleLoginPage);

app.post("/login", handleLogin);

app.post("/logout", requireAuth, handleLogout);

app.get("/", requireAuth, handleMap);

app.get("/index.html", requireAuth, handleMap);
app.get("/locations/venue-route.json", requireAuth, handleVenueRoute);
app.get("/shrine/images/:imageName", requireAuth, handleShrineImage);

app.listen(PORT, () => {
  console.log(`Shrines map server listening on port ${PORT}`);
});
