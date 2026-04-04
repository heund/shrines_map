const { buildClearSessionCookie } = require("../lib/vercel-auth");

module.exports = async (_req, res) => {
  res.setHeader("Set-Cookie", buildClearSessionCookie());
  res.writeHead(302, { Location: "/login" });
  return res.end();
};
