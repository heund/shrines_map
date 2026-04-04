const fs = require("fs");
const path = require("path");

const INDEX_PATH = path.join(__dirname, "..", "index.html");
const INDEX_HTML_TEMPLATE = fs.readFileSync(INDEX_PATH, "utf8");

function renderIndexHtml(googleMapsApiKey) {
  if (!googleMapsApiKey) {
    throw new Error("Missing required environment variable: GOOGLE_MAPS_API_KEY");
  }

  const injectedApiKeyLiteral = JSON.stringify(googleMapsApiKey);
  const renderedHtml = INDEX_HTML_TEMPLATE.replace(
    /const googleMapsApiKey = ".*?";/,
    `const googleMapsApiKey = ${injectedApiKeyLiteral};`
  );

  if (renderedHtml === INDEX_HTML_TEMPLATE) {
    throw new Error("Failed to inject GOOGLE_MAPS_API_KEY into index.html");
  }

  return renderedHtml;
}

module.exports = {
  renderIndexHtml
};
