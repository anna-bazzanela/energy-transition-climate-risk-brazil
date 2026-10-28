# Observed climate extremes and electricity grid exposure in Brazil

Python code for calculating and mapping observed trends in precomputed ETCCDI
climate indices over Brazil, with optional electricity infrastructure overlays.
The supplied research script is attributed to Anna Carolina Bazzanela.

**Start here:** [How to publish this repository on GitHub](docs/GITHUB_GUIDE.md).

## Scope

This repository documents the **observed-trend component** of a study on climate
extremes and Brazil's energy transition. The supplied active script maps **TNx
and TXx** from previously calculated NetCDF trend and p-value files.

The refactored script can calculate trends from annual index fields and produce
maps. Configuration entries for PRCPTOT, R95p and CDD are also provided for use
with externally prepared annual index files. These entries do not establish
that precipitation results in the manuscript have been reproduced here.

**Not included:** daily-to-index calculations using xclim, CMIP6 downloads,
regridding, future-minus-historical changes, ensemble means, model agreement,
or quantitative distribution-grid vulnerability calculations. Those steps are
described in the supplied methodology but their source code was not supplied.
The manuscript should describe the repository's scope accordingly.

## Files

| File or directory | Purpose |
| --- | --- |
| `spatial_trends_ppe.py` | Configurable observed-trend calculation and maps |
| `config.example.toml` | Example for new computations and raw p values |
| `config.legacy.example.toml` | Plot-only example for original masked p values |
| `requirements.txt`, `environment.yml` | Supported Python environment |
| `CITATION.cff` | Software citation metadata |
| `docs/METHODS.md` | Methodology summary and implementation boundaries |
| `docs/DATA.md` | Input structure, sources and missing provenance |
| `docs/REPRODUCIBILITY.md` | Differences from the supplied script and validation |
| `docs/GITHUB_GUIDE.md` | Beginner upload, versioning and DOI instructions |
| `docs/SUBMISSION_TEXT.md` | Conditional code-availability wording |
| `legacy/` | Sanitized source snapshot with historical plotting behavior |
| `examples/`, `tests/` | Synthetic example and numerical regression tests |

## Installation

Use Python **3.11 or newer**; Python 3.12 is the preparation test environment.
From the extracted repository folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, create the environment using `py -3 -m venv .venv` and activate it
in PowerShell with `.venv\Scripts\Activate.ps1` before installing requirements.
An alternative, when Conda is already installed, is:

```bash
conda env create -f environment.yml
conda activate climate-grid-trends
```

The dependency ranges support this refactor; they do not identify the exact
package versions used for the original manuscript. Actual run versions are
written to the output run record. `docs/validation-environment.txt` records the
environment used for preparation tests, not an original research environment.

## Try the synthetic example first

```bash
python examples/create_demo.py
python spatial_trends_ppe.py --config demo_config.toml --stage all
python -m unittest discover -s tests -v
```

The example creates artificial annual temperatures and a rectangular mask.
It uses no observed data, actual Brazil boundary, or infrastructure inventory.
Its PNG maps verify software execution only and are not research findings.

## Run with research data

1. Copy `config.example.toml` to `config.toml`.
2. Place annual index files under `data/indices/` and set their variable names.
3. Supply a valid Brazil polygon with a defined CRS. If the file contains
   several countries, select Brazil with `mask.column` and `mask.value`.
4. Confirm the study period, annual aggregation, units, missing-data settings,
   and optionally the Brazilian region/infrastructure layers.
5. Run one of the following commands.

```bash
# Compute observed trends without requiring GIS files or Cartopy downloads.
python spatial_trends_ppe.py --config config.toml --stage compute

# Compute and map fresh trends and unmasked p values.
python spatial_trends_ppe.py --config config.toml --stage all
```

For original precomputed files:

```bash
# First copy config.legacy.example.toml to config.legacy.toml and edit paths.
python spatial_trends_ppe.py --config config.legacy.toml --stage plot
```

For mapping newly computed files later, set `trend_pattern` and `pvalue_pattern`
to the corresponding `outputs/trend/` and `outputs/pvalue/` paths, and use
`pvalue_semantics = "raw"`.

All relative paths are resolved against the configuration file's directory.
No external climate datasets are downloaded by these commands. Cartopy may
download Natural Earth map layers on first use; set `natural_earth = false`
for offline plotting with only your own GIS layers.

## Outputs and statistical interpretation

- `outputs/trend/{index}_dec_trend_BR.nc`: Sen slope per decade.
- `outputs/pvalue/{index}_dec_pvalue_BR.nc`: complete, unmasked MK p values.
- `outputs/count/{index}_dec_count_BR.nc`: finite annual sample count.
- `outputs/figures/{index}-SpatialTrend_decade_BR.png`: masked maps.
- `outputs/run_record_{stage}.json`: configuration, package versions and input checksums.

Computed NetCDF fields cover the configured rectangular extent; the country
mask is applied to maps, not to those saved fields. Outside-country values may
remain in the NetCDF if present in the input.

By default **stippling marks non-significant trends, p > 0.05**, consistent with
the intent of the supplied source. To stipple significant trends, use
`hatch = "significant"` with complete raw p values. Missing p values are never
treated as significant. Original MK does not correct for serial dependence or
multiple comparisons. See [method details](docs/METHODS.md).

## Data, citation and license

Research datasets and GIS layers were not attached and are not distributed.
Source links and the input contract appear in [the data guide](docs/DATA.md).
The exact research file versions and original environment still need recording.

`CITATION.cff` contains a provisional software citation. Verify software authors,
add the real repository URL and release date, and add a DOI only after it exists.
No manuscript publication details have been inferred.

A reuse license has not yet been selected. See [licensing guidance](LICENSE_NOTICE.md).
Before submission, compare the refactor with the original research files and
freeze the checked version as a GitHub release. Synthetic tests alone do not
verify the manuscript's results.
