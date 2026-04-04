const {
  buildSessionCookie,
  createSessionToken
} = require("../lib/vercel-auth");

async function readPasswordFromRequest(req) {
  if (req.body && typeof req.body === "object") {
    return String(req.body.password || "");
  }

  const chunks = [];

  for await (const chunk of req) {
    chunks.push(chunk);
  }

  const rawBody = Buffer.concat(chunks).toString("utf8");
  const formData = new URLSearchParams(rawBody);
  return String(formData.get("password") || "");
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.writeHead(302, { Location: "/login" });
    return res.end();
  }

  const mapPassword = process.env.MAP_LOGIN_PASSWORD;

  if (!mapPassword) {
    return res.status(500).send("Missing required environment variable: MAP_LOGIN_PASSWORD");
  }

  const password = await readPasswordFromRequest(req);

  if (password !== mapPassword) {
    res.writeHead(302, { Location: "/login?error=1" });
    return res.end();
  }

  const token = await createSessionToken();
  res.setHeader("Set-Cookie", buildSessionCookie(token));
  res.writeHead(302, { Location: "/" });
  return res.end();
};
