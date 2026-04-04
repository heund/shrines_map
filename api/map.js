const { renderIndexHtml } = require("../lib/render-index-html");
const { readSession } = require("../lib/vercel-auth");

module.exports = async (req, res) => {
  if (!(await readSession(req))) {
    res.writeHead(302, { Location: "/login" });
    return res.end();
  }

  const googleMapsApiKey = process.env.GOOGLE_MAPS_API_KEY;

  if (!googleMapsApiKey) {
    return res.status(500).send("Missing required environment variable: GOOGLE_MAPS_API_KEY");
  }

  res.setHeader("Cache-Control", "no-store");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.status(200).send(renderIndexHtml(googleMapsApiKey));
};
