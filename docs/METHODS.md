# Methodology and implemented scope

This summary follows the supplied methodology document. It separates the study
design from the code actually provided. It does not replace the article's full
reference list or provide missing daily-index/projection implementations.

## Study design reported in the methodology

Observed daily data are from BR-DWGD at approximately 10 km horizontal resolution,
for 1961–2023. The methodology reports ETCCDI calculations using Python and xclim,
linking to [xclim v0.32.1 documentation](https://xclim.readthedocs.io/en/v0.32.1/indices.html).
A documentation link alone does not establish the installed version used.

| Index | Definition in the supplied methodology | Unit |
| --- | --- | --- |
| TXx | Highest daily maximum temperature in the month | °C |
| TNx | Highest daily minimum temperature in the month | °C |
| PRCPTOT | Annual precipitation total on days with precipitation > 1 mm | mm |
| R95p | Annual precipitation total on days above the 95th percentile | mm |
| CDD | Maximum consecutive days with precipitation < 1 mm | days |

**Aggregation must be confirmed:** the source's disabled calculation block
expects `{index}_annual_obs.nc`, while the supplied table describes monthly TXx
and TNx. The refactor explicitly requires annual fields and does not choose how
monthly values are aggregated. Confirm that the manuscript and input files use
the same definition. Also confirm the strict `> 1 mm` PRCPTOT threshold, the
R95p reference period/wet-day threshold, and CDD year-boundary handling against
the original index-generation settings. No undocumented convention is imposed.

The reported CMIP6 workflow uses twelve models, SSP2-4.5 and SSP5-8.5,
bilinear interpolation to a common 1° grid, index calculation for each model,
and an ensemble mean. Future changes compare 2025–2055 with 1995–2014.
Agreement of at least eight of twelve models on the sign of change is the
reported robustness criterion. These operations are **not implemented** here.

Model identifiers are transcribed below as supplied; verify exact ESGF source
IDs and dataset versions before building a machine-readable download workflow.

| Model label supplied | Ensemble member |
| --- | --- |
| ACCESS-ESM1-5 | r1i1p1f1 |
| CanESM5 | r1i1p1f1 |
| CMCC-ESM2 | r1i1p1f1 |
| CNRM-ESM2-1 | r1i1p1f2 |
| EC-EARTH3 | r1i1p1f1 |
| HADGEM3-GC31-LL | r1i1p1f3 |
| INM-CM5-0 | r1i1p1f1 |
| KACE-1-0-G | r1i1p1f1 |
| MIROC6 | r1i1p1f1 |
| MPI-ESM1-2-HR | r1i1p1f1 |
| MRI-ESM-2.0 | r1i1p1f1 |
| TaiESM1.0 | r1i1p1f1 |

The narrative review relates climate extremes to energy transition technologies
using PLANTE and material from EPE, ANEEL, MME and scientific literature. It is a
qualitative assessment; this repository does not compute outage probabilities,
asset failure rates, or a composite vulnerability index. The supplied GIS
overlays are transmission lines and substations, which alone are not a detailed
inventory of distribution-grid assets.

## Observed trends implemented here

For each grid point, the new calculation reads annual index values in chronological
order and applies the **original Mann–Kendall test** with two-sided p values and
alpha = 0.05 by default. The implementation uses `pymannkendall.original_test`.
Finite observations are retained; a configurable minimum of 30 valid years is
an added coverage rule, not a threshold recovered from the original source.

The Sen slope is the median of `(value[j] - value[i]) / (year[j] - year[i])` for
all pairs with `j > i`, multiplied by ten. SciPy's `theilslopes` receives actual
calendar years, retaining elapsed time when a cell has missing observations.
For a regular annual time axis, this agrees with pyMannKendall 1.4.3's
sample-index slope multiplied by ten, within numerical tolerance, including
series with NaNs retained at their annual positions. The new implementation
does not imply that the source package necessarily compressed those gaps.

For a constant series with sufficient valid data, the slope is zero and p = 1.
Insufficient coverage yields missing slope/p values and a retained sample count.
All annual timestamps must be present in the configured period; individual
grid cells may contain NaNs. Multiple samples per year are rejected.

No prewhitening, serial-correlation adjustment, spatial field-significance test
or multiple-testing correction is applied. The statistical test therefore
retains the independence limitation described in the original MK method;
the code does not claim those issues have been resolved.

## Spatial display and p-value semantics

The main script normalizes longitude to −180…180 and sorts both axes. It uses
a polygon selected by a named attribute, or a file containing Brazil only.
Grid centers intersecting the country polygon are retained; there is no
fractional-area weighting. Optional vector layers are reprojected to EPSG:4326.

The supplied source hides p <= 0.05 as NaN, then draws hatching over remaining
p values. Therefore, its intended hatching convention is **non-significance**.
NaNs in those original files conflate significance and invalid/missing tests.

New outputs retain all p values. Legacy plotting is supported by an explicit
`legacy-nonsignificant` setting, which cannot reconstruct significant cells.
Requesting significant hatching from those legacy files raises an error.
The numerical fields are never inferred from a rendered image.

## Method references

- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13, 245–259.
  https://doi.org/10.2307/1907187
- Kendall, M. G. (1975). *Rank Correlation Methods*, 4th edition. Charles Griffin.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau.
  *Journal of the American Statistical Association*, 63, 1379–1389.
  https://doi.org/10.1080/01621459.1968.10480934
- pyMannKendall implementation and limitations:
  https://github.com/mmhs013/pyMannKendall
- SciPy implementation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html

Retain the article's original numbered citations when editing the manuscript;
this repository does not attempt to reconstruct references [12]–[26] from numbers.
