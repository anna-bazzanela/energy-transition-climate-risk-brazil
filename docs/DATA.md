# Data requirements and provenance

No research NetCDF files or GIS layers were supplied with the source code.
Do not treat example filenames as available datasets. The synthetic example
creates its own artificial inputs and is separate from the study data.

## Annual index files

By default the code expects `data/indices/TNx_annual_obs.nc` and
`data/indices/TXx_annual_obs.nc`. Configure other names using `annual_pattern`.
Each file must contain:

- One explicitly configured data variable (for example `TNx`).
- Exactly the dimensions `time`, `lat`, `lon`; `latitude`/`longitude` are accepted aliases.
- Decoded datetime coordinates with one sample for every year of the selected period.
- A rectilinear grid with finite, unique coordinates. Both latitude orders and
  −180…180/0…360 longitudes are supported; duplicate longitude seam points are rejected.
- Finite index values or NaN. The original index-generation missing-day quality
  checks must already have been applied upstream.

Typical annual input: `TNx(time=63, lat=..., lon=...)`, for 1961–2023 inclusive.
Extra dimensions such as `percentiles`, `member` or `height` must be selected
explicitly before use. The script does not silently average or select them.
Temperature can be in °C or K for slope calculation because a constant offset
does not change the slope; convert other units explicitly upstream. R95p must
be an accumulated amount in mm, not a fraction of total rainfall.

## Existing trend and p-value files

For original plot-only execution:

| File | Expected variable | Required interpretation |
| --- | --- | --- |
| `data/precomputed/trend/TNx_dec_trend_BR.nc` | `trends` | Slope already expressed per decade |
| `data/precomputed/pvalue/TNx_dec_pvalue_BR.nc` | `pvalues` | Original files retain only p > alpha |
| Equivalent TXx files | Same variables | Same conventions |

Both variables must have only `lat`, `lon` dimensions with identical coordinate
values after normalization. These data are not interpolated by the plotting
stage. Full p-value files require `pvalue_semantics = "raw"`; original masked
files require `"legacy-nonsignificant"`. Verify that the original alpha was 0.05
and that the NetCDF time period matches the figure description. Plot-only mode
does not recover the original period from annual data.

## GIS inputs

`country_shape` is required for maps. Use a polygon file containing Brazil only,
or a multi-country layer with an explicit selection, for example:

```toml
[mask]
column = "ADMIN"
value = "Brazil"
```

`ADMIN` is an example, not an assumed field in your original shapefile. Inspect
your own fields using `python -c "import geopandas as g; print(g.read_file('data/shapes/brazil.gpkg').columns)"`.

Optional paths are `regions_shape` (Brazilian region outlines),
`transmission_shape` (line overlay) and `substations_shape` (points).
All layers require their correct CRS. For shapefiles, retain at least the
`.shp`, `.shx`, `.dbf` and `.prj` files together, plus `.cpg` when supplied.
Do not assign WGS84 to a layer that was actually created in another CRS.

## Sources

BR-DWGD source and citation:

- [Author-maintained dataset page](https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data).
- [Author-maintained download repository](https://github.com/AlexandreCandidoXavier/BR-DWGD).
- Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022).
  New improved Brazilian daily weather gridded data (1961–2020).
  *International Journal of Climatology*, 42, 8390–8404. https://doi.org/10.1002/joc.7731

The current data page extends beyond the 1961–2023 period in the supplied
methodology. Use the exact research version and period; a newer download must
not silently replace the original files. Exact BR-DWGD version: **not supplied**.

The original filenames identify region, South America, ocean, transmission and
substation layers, but do not establish their providers, publication dates or
licenses. Record the original download links and dates before claiming exact
reproducibility. ANEEL's [open-data portal](https://dadosabertos.aneel.gov.br/)
is a relevant institutional starting point, not confirmation of the provenance
of the particular layers used in the research. Cartopy's optional basemap uses
[Natural Earth](https://www.naturalearthdata.com/).

CMIP6 data are outside the implemented scope. For the full study, additionally
record model source ID, member, experiment, grid label, variable, frequency,
calendar, version, download node and input checksums for every model.

## Provenance record to complete

For each research input, record its exact filename, provider URL or DOI, dataset
version, access date, temporal range, spatial grid, units, preprocessing, and
redistribution terms. The refactor writes SHA-256 checksums and package versions
after a successful run. Run records can contain local configured paths; review
them before any deliberate publication. Data and output folders are excluded
from Git by default. Git ignore rules do not apply to a manual browser upload.
