# Preparation validation

Checked on October 27, 2026, using Python 3.12 on Linux. Exact installed package
versions are recorded in `docs/validation-environment.txt`.

| Check | Outcome |
| --- | --- |
| Numerical and input-validation tests | 19 passed |
| Complete annual series against pyMannKendall 1.4.3 | Slope and p values agree within test tolerance |
| Regular annual series with NaNs against pyMannKendall 1.4.3 | Slope and p values agree within test tolerance |
| Known positive trend, constant series, missing/insufficient data | Passed |
| Monthly input and missing annual timestamps | Rejected as intended |
| Longitude normalization and reversed latitude | Passed |
| Duplicate longitude seam | Rejected as intended |
| Raw and original-style masked p-value classifications | Passed |
| Significant hatching requested from legacy masked files | Rejected as intended |
| Synthetic annual input → trends → NetCDF → TNx/TXx PNG | Completed |
| Plot-only execution on fresh raw files | Completed |
| Plot-only execution on simulated original-style masked files | Completed |
| Synthetic map layout | Both output maps visually inspected |
| Saved synthetic NetCDF fields | Expected dimensions and valid p-value range |
| Both example TOML files | Parsed successfully |
| Citation file | YAML parsed and basic identity fields checked; no full CFF schema validation |
| Python source files, including sanitized reference | Compiled successfully |
| Local Markdown file links | Resolved successfully |

The synthetic example uses generated temperatures and a rectangular geometry.
No original BR-DWGD inputs, infrastructure layers, or manuscript figures were
available. The original calculation environment is unknown. The original
reference script was syntax-checked, not executed against research data.
The GitHub Actions workflow is provided but has not been executed on GitHub.
Natural Earth downloads, the original GIS inventories, macOS/Windows execution,
and the alternative Conda environment have not been tested during preparation.

No empirical claim of full manuscript reproduction is made. Research-data
validation and release metadata should be completed by the author before
freezing the software version cited in the submission.
