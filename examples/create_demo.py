#!/usr/bin/env python3
"""Create deterministic artificial inputs. These are not research data."""
from pathlib import Path
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "demo_data"
    output.mkdir(exist_ok=True)
    lat, lon = np.linspace(-33, 8, 10), np.linspace(-74, -31, 12)
    time = pd.date_range("1961-01-01", "2023-01-01", freq="YS")
    years = np.arange(len(time))[:, None, None]
    rng = np.random.default_rng(24601)
    slope = np.linspace(-0.05, 0.09, len(lon))[None, None, :]
    for index, base in (("TNx", 22.0), ("TXx", 35.0)):
        values = base + slope * years + rng.normal(0, 0.6, (len(time), len(lat), len(lon)))
        values[10:15, 4, 4] = np.nan
        ds = xr.Dataset({index: (("time", "lat", "lon"), values)},
                        coords={"time": time, "lat": lat, "lon": lon},
                        attrs={"data_type": "SYNTHETIC DEMONSTRATION ONLY"})
        ds[index].attrs["units"] = "degC"
        ds.to_netcdf(output / f"{index}_annual_obs.nc")
    gpd.GeoDataFrame({"name": ["Synthetic rectangular mask"]},
                     geometry=[box(-73, -30, -35, 5)], crs="EPSG:4326").to_file(
        output / "synthetic_country.geojson", driver="GeoJSON")
    config = (ROOT / "config.example.toml").read_text(encoding="utf-8")
    config = config.replace('"data/indices/{index}_annual_obs.nc"', '"demo_data/{index}_annual_obs.nc"')
    config = config.replace('output_dir = "outputs"', 'output_dir = "demo_outputs"')
    config = config.replace('"data/shapes/brazil.gpkg"', '"demo_data/synthetic_country.geojson"')
    config = config.replace('font_family = "Times New Roman"', 'font_family = "DejaVu Serif"')
    config = config.replace('natural_earth = true', 'natural_earth = false')
    (ROOT / "demo_config.toml").write_text(config, encoding="utf-8")
    print("Created SYNTHETIC inputs and demo_config.toml; no observed data were used.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
