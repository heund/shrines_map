const fs = require("fs");
const path = require("path");

const { readSession } = require("../lib/vercel-auth");

const LOGIN_PATH = path.join(__dirname, "..", "public", "login.html");
const LOGIN_HTML = fs.readFileSync(LOGIN_PATH, "utf8");

module.exports = async (req, res) => {
  if (await readSession(req)) {
    res.writeHead(302, { Location: "/" });
    return res.end();
  }

  res.setHeader("Cache-Control", "no-store");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.status(200).send(LOGIN_HTML);
};
