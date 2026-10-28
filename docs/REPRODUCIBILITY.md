# Reproducibility and source review

## Evidence available

The preparation used the supplied `spatial_trends_ppe.py` and methodology
document. No climate inputs, GIS data, original output maps, index-generation
scripts or projection scripts were attached. The supplied source checksum is
recorded in `SOURCE_PROVENANCE.json`; the reference copy is deliberately sanitized
and is not byte-identical to the uploaded source.

## Source findings

| Item | Supplied source | Prepared version |
| --- | --- | --- |
| Active computation | Plot existing TNx and TXx trends | Same indices by default, with separate new compute stage |
| Statistical calculation | Annual calculation is inside a disabled string block | Callable calculation on explicit annual input |
| Study period | Not explicitly selected in the source calculation | Configurable 1961–2023, following supplied methodology |
| Input variable | First data variable | Explicit variable name |
| Missing values | Broad exception handling; no minimum sample rule | Minimum valid-year threshold; logged failures |
| Sen slope | pyMannKendall slope per sample × 10 | Calendar-year pairwise slope × 10 |
| MK p values | Significant p values replaced by NaN | Raw p values retained in new computations |
| Stippling | Intended non-significant cells | Explicit non-significant convention by default |
| Brazil mask | Polygon number 2 | Selected named country or Brazil-only polygon |
| Coordinate handling | Assumes coordinate order and lon range | Sorted coordinates, normalized longitudes, exact alignment |
| Infrastructure | Required hardcoded layers | Optional layers with CRS handling |
| Maps | Fixed layout and local ocean polygon | Explicit extent, configurable map layers and explanatory caption |
| Provenance | Not written | Configuration, input hashes and package versions |

The supplied active code did not calculate the regional means stored in its
empty DataFrames. No regional statistics are claimed here.

## Interpretation of changes

Refactoring introduces behavior changes that may affect figures, especially
through the new minimum-coverage rule, country boundaries and color bins. The source used
Matplotlib's automatic normalization for temperature; the refactor uses explicit
boundary normalization. It retains the source palette family and level limits,
but does not promise pixel-identical colors, fonts, stippling or layout.

No unit conversion or annual aggregation is silently performed. The raw input
must already match the intended index definition. This matters because the
methodology describes monthly TNx/TXx but the source calculation names annual
inputs. The R95p percentile baseline and precipitation processing are absent.

## Verification performed during preparation

See `VALIDATION.md` for actual checks and outcomes. Tests use synthetic data and
known numerical expectations, including comparison with the original
pyMannKendall slope for a complete annual series. Synthetic map execution is
performed without Natural Earth downloads. These checks verify software
behavior, not the published scientific results.

## Compare against the manuscript before freezing a release

1. Record the exact original input versions, annual aggregation and environment.
2. Run plot-only mode on the original trends/p values using the correct semantics.
3. Confirm the source's polygon number 2 actually represented Brazil; use the
   correct feature in the refactor and record any boundary differences.
4. Recompute a few complete annual grid cells and compare slope and p values
   with the source calculation, then compare full fields and finite-data masks.
5. Examine cells with NaNs separately and document the new minimum-sample rule.
   On a regular annual axis, pyMannKendall 1.4.3 retains the original NaN positions
   for its slope calculation, and the tested slopes agree with the refactor.
   The source's original installed version was not supplied.
6. Compare map extent, levels, country coverage, stippling and infrastructure.
7. Save the exact run configuration, dependency versions, input checksums and
   figure-to-command mapping with the research record.
8. Update the repository validation statement and freeze the checked commit.

If the repository is intended to reproduce the entire paper, also supply the
daily-index calculations, CMIP6 preprocessing, projection/ensemble/model-agreement
code, data manifests and all remaining figure scripts. Until then, describe it
as the code for the observed-trend component only.
