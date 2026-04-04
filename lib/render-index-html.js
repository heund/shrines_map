const fs = require("fs");
const path = require("path");

const INDEX_PATH = path.join(__dirname, "..", "index.html");
const INDEX_HTML_TEMPLATE = fs.readFileSync(INDEX_PATH, "utf8");

function renderIndexHtml(googleMapsApiKey) {
  if (!googleMapsApiKey) {
    throw new Error("Missing required environment variable: GOOGLE_MAPS_API_KEY");
  }

  const apiKeyPattern = /const\s+googleMapsApiKey\s*=\s*(["']).*?\1;/;

  if (!apiKeyPattern.test(INDEX_HTML_TEMPLATE)) {
    throw new Error("Failed to locate googleMapsApiKey in index.html");
  }

  const injectedApiKeyLiteral = JSON.stringify(googleMapsApiKey);
  const renderedHtml = INDEX_HTML_TEMPLATE.replace(apiKeyPattern, `const googleMapsApiKey = ${injectedApiKeyLiteral};`);

  return renderedHtml;
}

module.exports = {
  renderIndexHtml
};
