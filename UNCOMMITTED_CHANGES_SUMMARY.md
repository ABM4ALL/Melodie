# Uncommitted Changes Summary

This repository currently contains uncommitted changes in the following areas:

## Core parallel execution

- Added `MelodieInfra/parallel/utils.py` to centralize parallel mode selection.
- Updated `Simulator`, `Trainer`, and `Calibrator` to support explicit `parallel_mode="process"` / `"thread"` overrides.
- Changed the default behavior so that, when `parallel_mode` is omitted, Melodie uses thread-based execution on Python 3.13+ and process-based execution on older versions.
- Removed the separate `Simulator.run_parallel_multithread()` entry point and folded thread execution into `Simulator.run_parallel()`.

## Runtime and test fixes

- Improved database error handling in `MelodieInfra/db/db.py` for pandas / SQLAlchemy compatibility.
- Updated simulator, trainer, and calibrator tests to match the new parallel execution API.
- Cleaned up pytest collection warnings by renaming helper classes in the test suite.
- Adjusted the calibrator test to work in environments where local process-based worker startup may be restricted.

## CI and workflow updates

- Updated `.github/workflows/test.yml` so the Python version matrix no longer stops early when one job fails.

## Documentation and examples

- Updated the tutorial, installation guide, changelog, and gallery pages to document the unified `run_parallel()` API and the current automatic backend-selection behavior.
- Regenerated the checked-in HTML documentation under `docs/html`.
- Updated example scripts and inline comments to use `run_parallel(..., parallel_mode="thread")` instead of the removed simulator-specific thread method.
- Kept example execution instructions aligned around `python -m examples...`.

## Example output artifacts

- The calibrator example currently has modified CSV outputs under `examples/covid_contagion_calibrator/data/output/` from recent local runs.

## Current validation status

- Full test suite currently passes locally: `65 passed`.
- Sphinx documentation build completes successfully and the checked-in HTML pages were rebuilt from the latest `docs/source` content.
