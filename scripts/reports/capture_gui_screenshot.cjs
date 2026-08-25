const { chromium } = require("C:\\Users\\30286\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\playwright");
const path = require("node:path");
const repoRoot = path.resolve(__dirname, "..", "..");

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1.5 });
  await page.goto("http://127.0.0.1:8765", { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForSelector('[data-testid="stAppViewContainer"]', { timeout: 60000 });
  await page.waitForTimeout(5000);
  await page.screenshot({
    path: path.join(repoRoot, "assets", "reports", "figures", "图5-2_系统GUI主要功能界面.png"),
    fullPage: true,
  });
  await browser.close();
})();
