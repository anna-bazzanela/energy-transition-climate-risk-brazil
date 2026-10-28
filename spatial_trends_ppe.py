#!/usr/bin/env python3
"""Observed ETCCDI trend calculation and mapping for Brazil.

Refactored from Anna Carolina Bazzanela's supplied research script.
See docs/REPRODUCIBILITY.md before comparing with manuscript figures.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import logging
from pathlib import Path
import platform
import sys
import tomllib

import numpy as np
import pymannkendall as mk
from scipy.stats import theilslopes
import xarray as xr

VERSION = "0.1.0"
LOG = logging.getLogger(__name__)
TEMPERATURE_COLORS = [
    "#3a54a4", "#5c90c2", "#90c3dd", "#c5e6f0", "#f0f9db", "#ffffff",
    "#ffffff", "#fff0a8", "#fdc778", "#f98e52", "#e54e35", "#bd1726",
]
PRECIPITATION_COLORS = [
    "#b05606", "#e68d23", "#fdca88", "#fde2bb", "#ffffff",
    "#ffffff", "#d9dbeb", "#c2bedc", "#887cb2", "#502382",
]
DRY_COLORS = [
    "#005046", "#1a7e76", "#58b0a7", "#a3dbd3", "#def0ed", "#ffffff",
    "#ffffff", "#f5efdc", "#ead59f", "#cfa256", "#a5691b", "#6e4007",
]


def trend_at_cell(values, years, min_valid=30, alpha=0.05):
    """Return Sen slope per decade, unmasked MK p value, and sample count.

    Actual years are used in pairwise slopes; missing observations do not
    compress time. MK is the original test, without autocorrelation correction.
    """
    values, years = np.asarray(values, float), np.asarray(years, float)
    valid = np.isfinite(values) & np.isfinite(years)
    y, x = values[valid], years[valid]
    n = len(y)
    if n < min_valid:
        return np.nan, np.nan, n
    if np.any(np.diff(x) <= 0):
        raise ValueError("Years must be strictly increasing.")
    if np.ptp(y) == 0:
        return 0.0, 1.0, n
    return float(theilslopes(y, x).slope * 10), float(mk.original_test(y, alpha).p), n


def normalize_grid(array):
    """Normalize a rectilinear grid to ascending lat/lon and -180..180 lon."""
    rename = {old: new for old, new in (("latitude", "lat"), ("longitude", "lon"))
              if old in array.dims and new not in array.dims}
    array = array.rename(rename)
    for name in ("lat", "lon"):
        if name not in array.coords or array[name].dims != (name,):
            raise ValueError(f"Expected a one-dimensional {name} coordinate.")
        if not np.isfinite(array[name].values).all():
            raise ValueError(f"Non-finite {name} coordinates are unsupported.")
    array = array.assign_coords(lon=((array.lon + 180) % 360) - 180)
    array = array.sortby("lat").sortby("lon")
    for name in ("lat", "lon"):
        if len(np.unique(array[name])) != array.sizes[name]:
            raise ValueError(f"Duplicate {name} coordinates; remove duplicate seam points first.")
    return array


def open_field(path, variable):
    """Load an explicitly named variable and close the underlying file."""
    with xr.open_dataset(path) as ds:
        if variable not in ds:
            raise ValueError(f"Variable {variable!r} missing in {path}; available: {list(ds.data_vars)}")
        return normalize_grid(ds[variable].load())


def annual_series(array, start, end, extent):
    """Select exactly one observation per year; reject monthly inputs/gaps."""
    if set(array.dims) != {"time", "lat", "lon"}:
        raise ValueError("Index input must have exactly the dimensions time, lat, lon.")
    try:
        years = array.time.dt.year.values
    except (AttributeError, TypeError) as exc:
        raise ValueError("Time must be a decoded NetCDF date coordinate.") from exc
    selected = np.flatnonzero((years >= start) & (years <= end))
    array = array.isel(time=selected).sortby("time")
    years = array.time.dt.year.values
    if not np.array_equal(years, np.arange(start, end + 1)):
        raise ValueError(f"Expected one sample per year for every year in {start}-{end}; "
                         "monthly inputs, missing years, or an incomplete period were found.")
    west, east, south, north = extent
    array = array.sel(lon=slice(west, east), lat=slice(south, north))
    if min(array.sizes["lat"], array.sizes["lon"]) < 2:
        raise ValueError("The selected extent must contain at least two latitudes and longitudes.")
    return array.transpose("time", "lat", "lon")


def compute_trends(array, min_valid, alpha, units):
    """Evaluate independent grid-cell tests using explicit calendar-year slopes."""
    years = array.time.dt.year.values
    values = array.values
    shape = values.shape[1:]
    slopes, pvalues = np.full(shape, np.nan), np.full(shape, np.nan)
    counts = np.zeros(shape, dtype="int32")
    for i in range(shape[0]):
        for j in range(shape[1]):
            slopes[i, j], pvalues[i, j], counts[i, j] = trend_at_cell(
                values[:, i, j], years, min_valid, alpha)
    coords = {"lat": array.lat, "lon": array.lon}
    ds = xr.Dataset({
        "trends": (("lat", "lon"), slopes),
        "pvalues": (("lat", "lon"), pvalues),
        "n_valid": (("lat", "lon"), counts),
    }, coords=coords)
    ds.trends.attrs.update(units=f"{units} decade-1", long_name="Sen slope per decade")
    ds.pvalues.attrs.update(units="1", long_name="Unmasked original Mann-Kendall p value")
    ds.n_valid.attrs.update(units="1", long_name="Number of finite annual observations")
    ds.attrs.update(
        software_version=VERSION, start_year=int(years[0]), end_year=int(years[-1]),
        alpha=alpha, min_valid_years=min_valid,
        trend_method="Median pairwise slopes against actual calendar year, multiplied by 10",
        significance_method="Original Mann-Kendall; no serial-correlation or multiple-testing correction",
        pvalue_semantics="raw",
    )
    return ds


def hatch_mask(pvalues, alpha, semantics, mode):
    """Never interpret missing p values as evidence of significance."""
    if semantics not in {"raw", "legacy-nonsignificant"}:
        raise ValueError("pvalue_semantics must be raw or legacy-nonsignificant.")
    if mode not in {"significant", "nonsignificant", "none"}:
        raise ValueError("hatch must be significant, nonsignificant, or none.")
    finite = np.isfinite(pvalues)
    if np.any(finite & ((pvalues < 0) | (pvalues > 1))):
        raise ValueError("Finite p values must fall within [0, 1].")
    if mode == "none":
        return np.zeros_like(pvalues, dtype=bool)
    if semantics == "legacy-nonsignificant":
        if mode == "significant":
            raise ValueError("Legacy files hide significant p values as NaN. "
                             "Recompute raw p values before hatching significant cells.")
        if np.any(finite & (pvalues <= alpha)):
            raise ValueError("Legacy p-value files must only retain values above alpha.")
        return finite & (pvalues > alpha)
    return finite & ((pvalues <= alpha) if mode == "significant" else (pvalues > alpha))


def load_vector(path, column="", value="", expected_type=None):
    """Read a GIS layer and select features by attribute, never by row number."""
    import geopandas as gpd
    frame = gpd.read_file(path)
    if frame.crs is None:
        raise ValueError(f"Missing CRS in {path}; define the source CRS before use.")
    if column:
        if column not in frame:
            raise ValueError(f"Column {column!r} not found in {path}; available: {list(frame.columns)}")
        frame = frame.loc[frame[column].astype(str).str.strip() == str(value).strip()]
    frame = frame.loc[frame.geometry.notna() & ~frame.geometry.is_empty].to_crs("EPSG:4326")
    if frame.empty:
        raise ValueError(f"No usable features selected from {path}.")
    if not frame.geometry.is_valid.all():
        raise ValueError(f"Invalid geometries in {path}; repair them explicitly before analysis.")
    if expected_type == "polygon" and not frame.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise ValueError(f"The country mask in {path} must contain only polygons.")
    return frame


def country_mask(array, frame):
    """Grid-center mask including boundary centers; no fractional-area weighting."""
    import shapely
    geometry = frame.geometry.union_all()
    lon, lat = np.meshgrid(array.lon.values, array.lat.values)
    mask = shapely.intersects_xy(geometry, lon, lat)
    if not mask.any():
        raise ValueError("Country geometry does not overlap any grid centers.")
    return xr.DataArray(mask, dims=("lat", "lon"), coords={"lat": array.lat, "lon": array.lon})


def path_for(config, name):
    value = config["paths"].get(name, "")
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else config["_root"] / path


def resolve_input(config, name, variable):
    path = path_for(config, name)
    if path is None:
        raise ValueError(f"Set paths.{name} in the configuration.")
    return Path(str(path).replace("{index}", variable))


def draw_map(config, index, trend, pvalue, semantics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import BoundaryNorm, ListedColormap
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    trend, pvalue = xr.align(trend, pvalue, join="exact")
    if set(trend.dims) != {"lat", "lon"} or set(pvalue.dims) != {"lat", "lon"}:
        raise ValueError("Precomputed trend and p-value fields must have only lat/lon dimensions.")
    trend, pvalue = trend.transpose("lat", "lon"), pvalue.transpose("lat", "lon")
    country = load_vector(path_for(config, "country_shape"),
                          config["mask"].get("column", ""), config["mask"].get("value", ""), "polygon")
    mask = country_mask(trend, country)
    trend, pvalue = trend.where(mask), pvalue.where(mask)
    settings = config["plot"]
    flags = hatch_mask(pvalue.values, config["analysis"]["alpha"], semantics, settings["hatch"])
    flags &= np.isfinite(trend.values)
    if not np.isfinite(trend.values).any():
        raise ValueError(f"No finite trend values within the selected country for {index}.")
    defaults = config["indices"][index]
    palette = defaults.get("palette", "temperature")
    colors = {"temperature": TEMPERATURE_COLORS, "precipitation": PRECIPITATION_COLORS,
              "dry": DRY_COLORS}[palette]
    cmap = ListedColormap(colors)
    limits = {"temperature": ("#313695", "#a50026"), "precipitation": ("#7f3b08", "#2d004b"),
              "dry": ("#003c30", "#543005")}[palette]
    cmap.set_under(limits[0]); cmap.set_over(limits[1])
    levels = defaults["levels"]
    norm = BoundaryNorm(levels, cmap.N)
    plt.rcParams.update({"font.family": settings["font_family"], "axes.unicode_minus": False})
    projection = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw={"projection": projection})
    try:
        ax.set_extent(config["analysis"]["extent"], crs=projection)
        ax.set_facecolor("#cdcdcd")
        field = ax.contourf(trend.lon, trend.lat, trend.values, transform=projection,
                            cmap=cmap, norm=norm, levels=levels, extend="both")
        if settings.get("natural_earth", True):
            ax.add_feature(cfeature.OCEAN.with_scale("50m"), facecolor="#83bade", zorder=2)
            ax.coastlines(resolution="50m", linewidth=0.8, zorder=3)
            ax.add_feature(cfeature.STATES.with_scale("50m"), edgecolor="gray", linewidth=0.5, zorder=3)
        ax.add_geometries(country.geometry, projection, facecolor="none", edgecolor="black", linewidth=1.1, zorder=4)
        regions = path_for(config, "regions_shape")
        if regions:
            layer = load_vector(regions)
            ax.add_geometries(layer.geometry, projection, facecolor="none", edgecolor="black", linewidth=1.5, zorder=4)
        if flags.any():
            ax.contourf(trend.lon, trend.lat, np.where(flags, 1.0, np.nan), levels=[0.5, 1.5],
                        colors="none", hatches=[".."], transform=projection, zorder=5)
        lines = path_for(config, "transmission_shape")
        if lines:
            layer = load_vector(lines)
            ax.add_geometries(layer.geometry, projection, facecolor="none", edgecolor="red", linewidth=0.7, alpha=0.5, zorder=6)
        substations = path_for(config, "substations_shape")
        if substations:
            layer = load_vector(substations)
            if not layer.geom_type.isin(["Point", "MultiPoint"]).all():
                raise ValueError("Substations must be point geometries.")
            points = layer.explode(index_parts=False)
            ax.scatter(points.geometry.x, points.geometry.y, transform=projection, c="#8C001A", s=14, marker="s", alpha=0.5, zorder=7)
        ax.set_title(index, fontsize=28, weight="bold")
        bar = fig.colorbar(field, ax=ax, ticks=levels, shrink=0.9, pad=0.025, aspect=25)
        bar.ax.tick_params(labelsize=13)
        bar.ax.set_title(defaults["trend_label"], fontsize=15, pad=12)
        if settings["hatch"] != "none":
            symbol = "<=" if settings["hatch"] == "significant" else ">"
            label = f"Stippling: p {symbol} {config['analysis']['alpha']:g} (original Mann-Kendall)"
            if semantics == "legacy-nonsignificant":
                label += "; missing p values are unclassified"
            fig.text(0.1, 0.06, label, fontsize=10)
        output = path_for(config, "output_dir") / "figures"
        output.mkdir(parents=True, exist_ok=True)
        filename = output / f"{index}-SpatialTrend_decade_BR.png"
        fig.savefig(filename, dpi=settings["dpi"], bbox_inches="tight")
        LOG.info("Saved %s", filename)
    finally:
        plt.close(fig)


def validate_config(config):
    analysis = config["analysis"]
    if not (0 < analysis["alpha"] < 1):
        raise ValueError("alpha must lie strictly between 0 and 1.")
    if analysis["end_year"] < analysis["start_year"]:
        raise ValueError("end_year must be at least start_year.")
    if not 3 <= analysis["min_valid_years"] <= analysis["end_year"] - analysis["start_year"] + 1:
        raise ValueError("min_valid_years must be between 3 and the period length.")
    extent = analysis["extent"]
    if len(extent) != 4 or not (-180 <= extent[0] < extent[1] <= 180 and -90 <= extent[2] < extent[3] <= 90):
        raise ValueError("extent must be [west, east, south, north] without a dateline crossing.")
    if config["plot"]["hatch"] not in {"significant", "nonsignificant", "none"}:
        raise ValueError("Unsupported hatch setting.")
    if config["precomputed"]["pvalue_semantics"] not in {"raw", "legacy-nonsignificant"}:
        raise ValueError("Unsupported pvalue_semantics setting.")
    for index in analysis["indices"]:
        defaults = config["indices"][index]
        levels = np.asarray(defaults["levels"], dtype=float)
        palette = defaults.get("palette", "temperature")
        sizes = {"temperature": 12, "precipitation": 10, "dry": 12}
        if palette not in sizes or len(levels) < 2 or len(levels) - 1 > sizes.get(palette, 0) or not np.isfinite(levels).all() or np.any(np.diff(levels) <= 0):
            raise ValueError(f"Invalid palette/levels for {index}.")
        for key in ("variable", "units", "trend_label"):
            if not defaults.get(key):
                raise ValueError(f"Set indices.{index}.{key}.")


def write_run_record(config, config_path, stage, inputs):
    """Record configuration and checksums of the actual input files used."""
    records = []
    for path in dict.fromkeys(inputs):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        records.append({"filename": path.name, "size_bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    versions = {}
    for package in ("numpy", "scipy", "xarray", "pandas", "pymannkendall", "matplotlib", "geopandas", "cartopy", "netCDF4", "shapely"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    settings = {key: value for key, value in config.items() if not key.startswith("_")}
    record = {"software_version": VERSION, "python": platform.python_version(), "stage": stage,
              "config_filename": config_path.name, "configuration": settings,
              "input_files": records, "package_versions": versions}
    (path_for(config, "output_dir") / f"run_record_{stage}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--stage", choices=["compute", "plot", "all"], default="all",
                        help="plot reads existing files; all plots freshly computed raw p values")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    try:
        with args.config.open("rb") as stream:
            config = tomllib.load(stream)
        config["_root"] = args.config.resolve().parent
        validate_config(config)
        output = path_for(config, "output_dir")
        if output is None:
            raise ValueError("Set paths.output_dir.")
        output.mkdir(parents=True, exist_ok=True)
        inputs = []
        if args.stage in {"plot", "all"}:
            country = path_for(config, "country_shape")
            if country is None:
                raise ValueError("Set paths.country_shape before mapping.")
            for name in ("country_shape", "regions_shape", "transmission_shape", "substations_shape"):
                path = path_for(config, name)
                if path:
                    if not path.is_file():
                        raise FileNotFoundError(path)
                    # Include required shapefile sidecars in provenance.
                    inputs.extend(sorted(path.parent.glob(path.stem + ".*")) if path.suffix.lower() == ".shp" else [path])
        for index in config["analysis"]["indices"]:
            LOG.info("Processing %s", index)
            if args.stage in {"compute", "all"}:
                filename = resolve_input(config, "annual_pattern", index)
                inputs.append(filename)
                array = open_field(filename, config["indices"][index]["variable"])
                analysis = config["analysis"]
                array = annual_series(array, analysis["start_year"], analysis["end_year"], analysis["extent"])
                result = compute_trends(array, analysis["min_valid_years"], analysis["alpha"], config["indices"][index]["units"])
                result.attrs["index"] = index
                result.attrs["source_filename"] = filename.name
                for folder, variable, suffix in (("trend", "trends", "trend"), ("pvalue", "pvalues", "pvalue"), ("count", "n_valid", "count")):
                    target = output / folder
                    target.mkdir(parents=True, exist_ok=True)
                    result[[variable]].to_netcdf(target / f"{index}_dec_{suffix}_BR.nc")
                trend, pvalue = result.trends, result.pvalues
                semantics = "raw"
            else:
                trend_path = resolve_input(config, "trend_pattern", index)
                pvalue_path = resolve_input(config, "pvalue_pattern", index)
                inputs.extend([trend_path, pvalue_path])
                trend = open_field(trend_path, config["precomputed"]["trend_variable"])
                pvalue = open_field(pvalue_path, config["precomputed"]["pvalue_variable"])
                semantics = config["precomputed"]["pvalue_semantics"]
            if args.stage in {"plot", "all"}:
                draw_map(config, index, trend, pvalue, semantics)
        write_run_record(config, args.config, args.stage, inputs)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        LOG.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
