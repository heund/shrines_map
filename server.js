const path = require("path");

const dotenv = require("dotenv");
const express = require("express");
const session = require("express-session");

const { renderIndexHtml } = require("./lib/render-index-html");

dotenv.config();

const app = express();
const PORT = Number(process.env.PORT || 3000);
const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const MAP_PASSWORD = process.env.MAP_LOGIN_PASSWORD;
const SESSION_SECRET = process.env.SESSION_SECRET;
const LOGIN_PATH = path.join(__dirname, "public", "login.html");
const SESSION_COOKIE_NAME = "shrines_map_session";

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
app.use(
  session({
    name: SESSION_COOKIE_NAME,
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    rolling: true,
    cookie: {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 1000 * 60 * 60 * 12
    }
  })
);

function isAuthenticated(req) {
  return req.session && req.session.isAuthenticated === true;
}

function requireAuth(req, res, next) {
  if (isAuthenticated(req)) {
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

function handleLoginPage(req, res) {
  if (isAuthenticated(req)) {
    return res.redirect("/");
  }

  setNoStore(res);
  return res.sendFile(LOGIN_PATH);
}

function handleLogin(req, res) {
  const password = String(req.body.password || "");

  if (password !== MAP_PASSWORD) {
    return res.redirect("/login?error=1");
  }

  req.session.isAuthenticated = true;
  return req.session.save((error) => {
    if (error) {
      return res.status(500).send("Failed to create session.");
    }
    return res.redirect("/");
  });
}

function handleLogout(req, res) {
  req.session.destroy((error) => {
    if (error) {
      return res.status(500).send("Failed to clear session.");
    }

    res.clearCookie(SESSION_COOKIE_NAME);
    return res.redirect("/login");
  });
}

function handleMap(_req, res) {
  setNoStore(res);
  res.type("html").send(renderIndexHtml(GOOGLE_MAPS_API_KEY));
}

app.get("/health", handleHealth);
app.get("/api/health", handleHealth);

app.get("/favicon.ico", (_req, res) => {
  res.status(204).end();
});

app.get("/login", handleLoginPage);
app.get("/api/login-page", handleLoginPage);

app.post("/login", handleLogin);
app.post("/api/login", handleLogin);

app.post("/logout", requireAuth, handleLogout);
app.all("/api/logout", requireAuth, handleLogout);

app.get("/", requireAuth, handleMap);

app.get("/index.html", requireAuth, handleMap);
app.get("/api/map", requireAuth, handleMap);

app.listen(PORT, () => {
  console.log(`Shrines map server listening on port ${PORT}`);
});
