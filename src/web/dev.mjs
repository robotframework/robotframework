// Development server: generates the fixtures listed in generate-testdata.mjs,
// runs Parcel, and regenerates a fixture whenever its library is saved so that
// the browser reloads with the new Libdoc spec.

import { spawn } from "node:child_process";
import { watch } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { generateOrWarn, FIXTURES } from "./generate-testdata.mjs";

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
 * The directory is watched rather than the files themselves, because editors
 * write a new file over the old one on save, which a file watch does not
 * survive. Only the fixture whose library was saved is regenerated, so working
 * on one library leaves the other's committed fixture alone.
 */
function watchLibraries() {
  const libraries = new Map(
    FIXTURES.map(({ library }) => [path.basename(library), library]),
  );
  const pending = new Map();
  for (const directory of new Set(
    FIXTURES.map(({ library }) => path.dirname(library)),
  )) {
    watch(directory, (_event, changed) => {
      const library = libraries.get(changed);
      if (!library) {
        return;
      }
      clearTimeout(pending.get(library));
      pending.set(
        library,
        setTimeout(
          () => generateOrWarn({ quiet: false, only: library }),
          DEBOUNCE_MS,
        ),
      );
    });
  }
}

await generateOrWarn();
watchLibraries();
startParcel();
