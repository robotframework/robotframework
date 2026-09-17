// Development server: generates libdoc/testdata.ts from libdoc/DevLibrary.py,
// runs Parcel, and regenerates the fixture whenever the library is saved so
// that the browser reloads with the new Libdoc spec.

import { spawn } from "node:child_process";
import { watch } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { generateOrWarn, LIBRARY } from "./generate-testdata.mjs";

const WEB_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEBOUNCE_MS = 100;

function startParcel() {
  const bin = path.join(
    WEB_DIR,
    "node_modules",
    ".bin",
    process.platform === "win32" ? "parcel.cmd" : "parcel",
  );
  const parcel = spawn(bin, { cwd: WEB_DIR, stdio: "inherit" });
  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.on(signal, () => parcel.kill(signal));
  }
  parcel.on("exit", (code, signal) => process.exit(signal ? 1 : code ?? 0));
  return parcel;
}

/**
 * The directory is watched rather than the file itself, because editors write
 * a new file over the old one on save, which a file watch does not survive.
 */
function watchLibrary() {
  const name = path.basename(LIBRARY);
  let pending;
  watch(path.dirname(LIBRARY), (_event, changed) => {
    if (changed !== name) {
      return;
    }
    clearTimeout(pending);
    pending = setTimeout(() => generateOrWarn({ quiet: false }), DEBOUNCE_MS);
  });
}

await generateOrWarn();
watchLibrary();
startParcel();
