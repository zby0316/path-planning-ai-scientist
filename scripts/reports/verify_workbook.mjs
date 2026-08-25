import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const qaDir = path.join(repoRoot, "assets", "reports", "qa", "workbook");
const inputPath = path.join(repoRoot, "evidence", "validated_experiments", "验证后实验结果.xlsx");
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));

const sheetInfo = workbook.worksheets.items.map((sheet, index) => ({
  index,
  name: sheet.name,
  usedRange: sheet.getUsedRange()?.address ?? null,
}));

const overview = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 12000,
  tableMaxRows: 4,
  tableMaxCols: 8,
  tableMaxCellChars: 80,
});
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
  maxChars: 6000,
});

await fs.writeFile(path.join(qaDir, "workbook_overview.ndjson"), overview.ndjson, "utf8");
await fs.writeFile(path.join(qaDir, "workbook_error_scan.ndjson"), errors.ndjson, "utf8");

const rendered = [];
for (const item of sheetInfo) {
  const safeName = item.name.replace(/[\\/:*?"<>|]/g, "_");
  const preview = await workbook.render({ sheetName: item.name, autoCrop: "all", scale: 0.8, format: "png" });
  const out = path.join(qaDir, `sheet_${safeName}.png`);
  await fs.writeFile(out, new Uint8Array(await preview.arrayBuffer()));
  rendered.push(out);
}

console.log(JSON.stringify({ sheetInfo, rendered, errorScan: errors.ndjson }, null, 2));
