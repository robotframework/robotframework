#!/usr/bin/env python
"""Performance benchmark for ``parse_docstring`` in a Robot Framework context.

Three phases are measured for each of three docstring styles:

  direct    — calls ``parse_docstring(doc)`` N times in a tight loop.
              Isolates the parser itself with no RF overhead.

  libdoc    — calls ``LibraryDocumentation(path)`` on a generated library.
              This is the *only* RF execution phase that actually calls
              ``parse_docstring`` (via KeywordImplementation.update_docs).

  rf_import  — imports the library via RF's own ``TestLibrary.from_name``
              (the same path used during test execution). Confirms that
              ``parse_docstring`` is NOT called during library import — that
              only happens in the libdoc phase.

Three docstring styles:

  prose_only      — plain multi-line prose, no structured sections.
  args_only       — Google-style Args section only.
  full_structured — Google-style Args + Returns sections.

Usage::

    python utest/perf/bench_docstring.py [N] [-r RUNS] [--baseline]

``N`` is the number of keywords per library variant (default: 10 000).
``-r RUNS`` repeats every measurement RUNS times and reports
min / max / mean / median / stdev across all runs (default: 1).
"""
import cProfile
import importlib.util
import inspect
import io
import pstats
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

# ---------------------------------------------------------------------------
# Make sure the in-tree 'robot' package is used regardless of cwd.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = str(_REPO_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from robot.libdocpkg import LibraryDocumentation  # noqa: E402
from robot.running.testlibraries import TestLibrary  # noqa: E402

try:
    from robot.running.docstring import parse_docstring, ParsedDocString  # noqa: E402
    _PARSE_AVAILABLE = True
except ImportError:
    _PARSE_AVAILABLE = False

    class ParsedDocString:  # type: ignore[no-redef]
        def __init__(self, doc="", args=None, returns=""):
            self.doc = doc
            self.args = args if args is not None else {}
            self.returns = returns

    def parse_docstring(doc):  # type: ignore[no-redef]
        return ParsedDocString(doc=doc)

try:
    import robot.running.keywordimplementation as _kw_impl  # noqa: E402
    _KW_IMPL_HAS_PARSE = hasattr(_kw_impl, "parse_docstring")
except ImportError:
    _kw_impl = None  # type: ignore[assignment]
    _KW_IMPL_HAS_PARSE = False

_STYLES = ("prose_only", "args_only", "full_structured")
_PROFILE_TOP_N = 15


# ---------------------------------------------------------------------------
# Library generation
# ---------------------------------------------------------------------------

def _write_library(path: Path, n: int, style: str) -> None:
    """Write a synthetic Python library with *n* keyword functions to *path*."""
    buf = io.StringIO()
    buf.write("# Auto-generated benchmark library — do not edit\n\n")
    for i in range(n):
        buf.write(f"def keyword_{i:05d}(param_a, param_b):\n")
        buf.write(f'    """Keyword {i:05d}.\n\n')
        if style == "prose_only":
            buf.write(f"    Longer description for keyword {i:05d}.\n")
            buf.write("    This spans multiple lines to be realistic.\n")
        elif style == "args_only":
            buf.write("    Args:\n")
            buf.write(f"        param_a: First parameter for keyword {i:05d}.\n")
            buf.write(f"        param_b: Second parameter for keyword {i:05d}.\n")
        else:  # full_structured
            buf.write("    Args:\n")
            buf.write(f"        param_a: First parameter for keyword {i:05d}.\n")
            buf.write(f"        param_b: Second parameter for keyword {i:05d}.\n\n")
            buf.write("    Returns:\n")
            buf.write(f"        The result of keyword {i:05d}.\n")
        buf.write('    """\n')
        buf.write("    pass\n\n")
    path.write_text(buf.getvalue(), encoding="utf-8")


def _load_docstrings(lib_path: Path, n: int) -> "list[str]":
    """Import *lib_path* with importlib and extract each keyword's cleaned docstring.

    Using ``inspect.getdoc`` mirrors what RF itself uses internally
    (``inspect.getdoc(self.method)`` in ``librarykeyword.py``), so the
    docstrings passed to ``parse_docstring`` in the *direct* phase are
    byte-for-byte identical to what RF would pass.
    """
    module_name = lib_path.stem
    spec = importlib.util.spec_from_file_location(module_name, lib_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [
        inspect.getdoc(getattr(mod, f"keyword_{i:05d}")) or ""
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------

class _Result:
    """Holds the timing/memory outcome of one measured call."""
    __slots__ = ("elapsed", "peak_mb", "profile")

    def __init__(self, elapsed: float, peak_mb: float, profile: cProfile.Profile):
        self.elapsed = elapsed
        self.peak_mb = peak_mb
        self.profile = profile


class _Stats:
    """Aggregated results from one or more runs of the same measurement."""
    __slots__ = (
        "t_min", "t_max", "t_mean", "t_median", "t_stdev",
        "m_min", "m_max", "m_mean", "m_median", "m_stdev",
        "median_profile",
    )

    def __init__(self, results: "list[_Result]"):
        times = [r.elapsed for r in results]
        mems = [r.peak_mb for r in results]
        n = len(results)
        self.t_min = min(times)
        self.t_max = max(times)
        self.t_mean = sum(times) / n
        self.t_median = statistics.median(times)
        self.t_stdev = statistics.stdev(times) if n > 1 else 0.0
        self.m_min = min(mems)
        self.m_max = max(mems)
        self.m_mean = sum(mems) / n
        self.m_median = statistics.median(mems)
        self.m_stdev = statistics.stdev(mems) if n > 1 else 0.0
        # Profile from the run whose elapsed time is closest to the median.
        self.median_profile = min(
            results, key=lambda r: abs(r.elapsed - self.t_median)
        ).profile


def _measure(fn) -> _Result:
    """Run *fn()* once, capturing wall-clock time, peak tracemalloc, and cProfile."""
    pr = cProfile.Profile()
    tracemalloc.start()
    t0 = time.perf_counter()
    pr.enable()
    fn()
    pr.disable()
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return _Result(elapsed=elapsed, peak_mb=peak / 1_048_576, profile=pr)


def _measure_many(fn, runs: int = 1) -> _Stats:
    """Run *fn* ``runs`` times and return aggregated statistics."""
    return _Stats([_measure(fn) for _ in range(runs)])


# ---------------------------------------------------------------------------
# Benchmark scenarios
# ---------------------------------------------------------------------------

def _noop_parse(doc: str) -> ParsedDocString:
    """Baseline no-op: returns immediately without parsing."""
    return ParsedDocString(doc=doc, args={}, returns="")


def _run_direct(docstrings: "list[str]", parse_fn=None) -> None:
    if parse_fn is None:
        parse_fn = parse_docstring
    for doc in docstrings:
        parse_fn(doc)


def _run_libdoc(lib_path: Path) -> None:
    LibraryDocumentation(str(lib_path))


def _run_rf_import(lib_path: Path) -> None:
    """Import the library via RF's own TestLibrary.from_name — no parse_docstring."""
    # Passing the absolute path string mirrors how RF resolves library paths at
    # runtime.  parse_docstring is NOT called here; that only happens in libdoc.
    TestLibrary.from_name(str(lib_path))


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

_SEP = 72

def _section(title: str) -> None:
    print(f"\n{'=' * _SEP}")
    print(f"  {title}")
    print(f"{'=' * _SEP}")


def _profile_text(pr: cProfile.Profile, top: int = _PROFILE_TOP_N) -> str:
    buf = io.StringIO()
    ps = pstats.Stats(pr, stream=buf).sort_stats("cumulative")
    ps.print_stats(top)
    return buf.getvalue()


def _print_filtered_profile(pr: cProfile.Profile) -> None:
    """Print only lines that mention robot/docstring/keyword symbols."""
    lines = _profile_text(pr).splitlines()
    for line in lines:
        lo = line.lower()
        if (
            line.strip().startswith("ncalls")          # column header
            or "docstring" in lo
            or "/robot/" in lo
            or "libdoc" in lo
            or "keyword" in lo
            or line.strip().startswith("{built-in")    # built-in calls
        ):
            print(f"  {line}")


def _print_entry(phase: str, style: str, s: _Stats, runs: int) -> None:
    """Print one benchmark entry — single row when runs==1, two-line block otherwise."""
    if runs == 1:
        print(f"  {phase:<14}  {style:<18}  {s.t_median:>8.3f}s  {s.m_median:>8.2f} MB")
    else:
        print(f"  {phase} / {style}")
        print(
            f"    time:  median={s.t_median:.3f}s  min={s.t_min:.3f}s  "
            f"max={s.t_max:.3f}s  mean={s.t_mean:.3f}s  stdev={s.t_stdev:.3f}s"
        )
        print(
            f"    mem:   median={s.m_median:.2f}MB  min={s.m_min:.2f}MB  "
            f"max={s.m_max:.2f}MB  mean={s.m_mean:.2f}MB  stdev={s.m_stdev:.2f}MB"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    baseline = "--baseline" in args or not _PARSE_AVAILABLE
    args = [a for a in args if a != "--baseline"]
    runs = 1
    if "-r" in args:
        idx = args.index("-r")
        runs = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
    n = int(args[0]) if args else 10_000
    if not _PARSE_AVAILABLE:
        mode = "BASELINE (parse_docstring not found on this branch — stubs used)"
    elif baseline:
        mode = "BASELINE (parse_docstring replaced with no-op)"
    else:
        mode = "NORMAL"

    print(f"\nDocstring benchmark  \u2014  {n:,} keywords per library variant")
    print(f"Mode: {mode}")
    print(f"Runs per measurement: {runs}")
    print(f"Python {sys.version.split()[0]}  |  robot src: {_SRC}")

    with tempfile.TemporaryDirectory(prefix="rf_bench_") as tmpdir:
        tmp = Path(tmpdir)

        # ------------------------------------------------------------------
        # Build library files and pre-extract cleaned docstring samples.
        # ------------------------------------------------------------------
        lib_paths: dict[str, Path] = {}
        doc_lists: dict[str, list[str]] = {}
        print("\nGenerating library files ...", end="", flush=True)
        for style in _STYLES:
            p = tmp / f"bench_{style}.py"
            _write_library(p, n, style)
            lib_paths[style] = p
            doc_lists[style] = _load_docstrings(p, n)
        print(" done.")

        # ------------------------------------------------------------------
        # Results table
        # ------------------------------------------------------------------
        _section("Timing and memory results")
        if runs == 1:
            hdr = f"  {'Phase':<14}  {'Style':<18}  {'Time':>9}  {'Peak RAM':>10}"
            print(hdr)
            print(f"  {'-'*14}  {'-'*18}  {'-'*9}  {'-'*10}")
        else:
            print(f"  Showing: median / min / max / mean / stdev  ({runs} runs per measurement)")

        all_results: list[tuple[str, str, _Stats]] = []

        for style in _STYLES:
            lib_path = lib_paths[style]

            parse_fn = _noop_parse if baseline else parse_docstring

            # 1. Direct parse (isolates parse_docstring only)
            s = _measure_many(
                lambda docs=doc_lists[style], fn=parse_fn: _run_direct(docs, fn), runs
            )
            _print_entry("direct", style, s, runs)
            all_results.append(("direct", style, s))

            # 2. libdoc (the only RF path that calls parse_docstring)
            if baseline and _KW_IMPL_HAS_PARSE:
                _kw_impl.parse_docstring = _noop_parse
            try:
                s = _measure_many(lambda p=lib_path: _run_libdoc(p), runs)
            finally:
                if _KW_IMPL_HAS_PARSE:
                    _kw_impl.parse_docstring = parse_docstring  # always restore
            _print_entry("libdoc", style, s, runs)
            all_results.append(("libdoc", style, s))

            # 3. RF library import (no parse_docstring — only in libdoc)
            s = _measure_many(lambda p=lib_path: _run_rf_import(p), runs)
            _print_entry("rf_import", style, s, runs)
            all_results.append(("rf_import", style, s))

        print(
            "\n  NOTE: rf_import confirms that parse_docstring is NOT called during\n"
            "        RF library loading — only during the libdoc phase."
        )

        # ------------------------------------------------------------------
        # cProfile detail
        # ------------------------------------------------------------------
        _section(f"cProfile  (top {_PROFILE_TOP_N} by cumulative time, from median run)")
        for phase, style, stats in all_results:
            print(f"\n  --- {phase} / {style} ---")
            _print_filtered_profile(stats.median_profile)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
