# Change log

## 0.1.0 — Prepared repository version

- Replaced personal machine paths with a TOML configuration and command-line interface.
- Added explicit compute, plot, and combined stages for observed annual indices.
- Preserved a sanitized reference of the supplied source under `legacy/`.
- Documented that the supplied active workflow plots TNx and TXx only.
- Saved complete p values for new runs and distinguished original masked files.
- Used calendar years for Sen slopes in the presence of missing observations.
- Added strict annual-frequency checks, a configurable valid-year threshold,
  explicit variable names, CRS checks, and country selection by attribute.
- Added optional infrastructure overlays, synthetic examples, tests and documentation.
- Added software citation metadata without inventing a repository URL or DOI.

This preparation is not evidence that manuscript results have been reproduced.
Compare the refactor with the original data before using it as the computational
record of the submitted figures. See `docs/REPRODUCIBILITY.md`.
