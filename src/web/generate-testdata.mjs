// Generates the fixtures rendered by `npm start`, by running Libdoc from this
// checkout on the libraries listed in FIXTURES. Add a case to the UI by adding a
// keyword to the library that covers it.
//
// Usage: node generate-testdata.mjs [--quiet]

import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as prettier from "prettier";

const WEB_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(WEB_DIR, "..", "..");
/**
 * One entry per fixture, generated and watched by the development server. They
 * are separate libraries rather than one, because a library has a single
 * documentation format and the formats are exactly what is being covered.
 *
 * Which fixture the page renders is decided in libdoc/libdoc.html, not here:
 * Parcel resolves imports statically, so that file spells out each output path
 * and the query value that selects it. Adding an entry here means adding a
 * branch there as well.
 */
const FIXTURES = [
  {
    library: path.join(WEB_DIR, "libdoc", "DevLibrary.py"),
    output: path.join(WEB_DIR, "libdoc", "testdata.ts"),
  },
  {
    library: path.join(WEB_DIR, "libdoc", "DevLibraryRobotFormat.py"),
    output: path.join(WEB_DIR, "libdoc", "testdata-robot.ts"),
  },
];
// Stands in for the generation time, see `normalize`.
const GENERATED = "2024-01-01T00:00:00+00:00";

/**
 * Libdoc has to come from this checkout rather than from an installed Robot
 * Framework, so the fixture always matches the sources the frontend is
 * developed against.
 */
function pythonExecutable() {
  const venv =
    process.platform === "win32"
      ? path.join(REPO_ROOT, ".venv", "Scripts", "python.exe")
      : path.join(REPO_ROOT, ".venv", "bin", "python");
  const python = existsSync(venv) ? venv : process.env.PYTHON || "python3";
  const version = spawnSync(
    python,
    ["-c", "import sys; print('.'.join(str(v) for v in sys.version_info[:2]))"],
    { encoding: "utf8" },
  );
  if (version.error || version.status !== 0) {
    throw new Error(
      `Running '${python}' failed: ${version.error?.message ?? version.stderr.trim()}`,
    );
  }
  const [major, minor] = version.stdout.trim().split(".").map(Number);
  if (!(major > 3 || (major === 3 && minor >= 12))) {
    throw new Error(
      `${python} is Python ${version.stdout.trim()}, but the type alias statements in DevLibrary.py need 3.12 or newer.`,
    );
  }
  return python;
}

function runLibdoc(python, library, specPath) {
  const args = [
    "-m",
    "robot.libdoc",
    path.relative(REPO_ROOT, library),
    specPath,
  ];
  const result = spawnSync(python, args, {
    cwd: REPO_ROOT,
    encoding: "utf8",
    env: { ...process.env, PYTHONPATH: path.join(REPO_ROOT, "src") },
  });
  if (result.error) {
    throw new Error(`Running '${python}' failed: ${result.error.message}`);
  }
  if (result.status !== 0) {
    const output = `${result.stdout}${result.stderr}`.trim();
    throw new Error(
      `${python} -m robot.libdoc exited with ${result.status}:\n${output}`,
    );
  }
}

/**
 * Drops everything that depends on the machine or the moment the fixture is
 * generated on, so that regenerating it produces a diff only when the library
 * itself changed. Line numbers are left alone: they depend on the library file
 * only.
 */
function normalize(value) {
  if (Array.isArray(value)) {
    return value.map(normalize);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [
        key,
        normalizeItem(key, item),
      ]),
    );
  }
  return value;
}

function normalizeItem(key, item) {
  if (typeof item === "string") {
    if (key === "source") {
      return path.relative(REPO_ROOT, item).split(path.sep).join("/");
    }
    // The generation time is the one value that differs on every run, and the
    // development server regenerates the fixture on every save, so keeping it
    // would leave the file permanently modified in the working tree. The
    // footer renders it, so it stays a date.
    if (key === "generated") {
      return GENERATED;
    }
  }
  return normalize(item);
}

async function generate({ quiet = false, only = null } = {}) {
  const python = pythonExecutable();
  const fixtures = only
    ? FIXTURES.filter((fixture) => fixture.library === only)
    : FIXTURES;
  for (const fixture of fixtures) {
    await generateFixture(python, fixture, quiet);
  }
}

async function generateFixture(python, fixture, quiet) {
  const library = path.basename(fixture.library);
  const output = path
    .relative(WEB_DIR, fixture.output)
    .split(path.sep)
    .join("/");
  const tmp = mkdtempSync(path.join(tmpdir(), "libdoc-testdata-"));
  try {
    const specPath = path.join(tmp, "spec.json");
    runLibdoc(python, fixture.library, specPath);
    const spec = normalize(JSON.parse(readFileSync(specPath, "utf8")));
    const source = [
      "// Development fixture rendered by `npm start`, generated with Libdoc from",
      `// libdoc/${library}. Add a case to the UI by adding a keyword there.`,
      "//",
      `// Do not edit by hand: run \`npm run testdata\`, or just save ${library}`,
      "// while `npm start` is running.",
      'import type { Libdoc } from "./types";',
      "",
      `const DATA: Libdoc = ${JSON.stringify(spec)};`,
      "",
      "export { DATA };",
      "",
    ].join("\n");
    const config = await prettier.resolveConfig(fixture.output);
    writeFileSync(
      fixture.output,
      await prettier.format(source, { ...config, filepath: fixture.output }),
    );
    if (!quiet) {
      const kws = spec.keywords.length;
      const types = spec.typedocs.length;
      console.log(
        `Generated ${output} from ${library}: ${kws} keywords, ${types} types.`,
      );
    }
  } finally {
    rmSync(tmp, { force: true, recursive: true });
  }
}

/**
 * A failure never stops the dev server: the previously generated fixtures are
 * committed, so the frontend still has something to render.
 */
async function generateOrWarn(options) {
  try {
    await generate(options);
    return true;
  } catch (error) {
    console.warn(
      `\n⚠ Could not generate the development fixtures, using the committed ones.\n${error.message}\n`,
    );
    return false;
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  await generateOrWarn({ quiet: process.argv.includes("--quiet") });
}

export { generate, generateOrWarn, FIXTURES };
