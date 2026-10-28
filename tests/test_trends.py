"""Numerical tests independent of the unavailable manuscript input files."""
import unittest

import geopandas as gpd
import numpy as np
import pandas as pd
import pymannkendall as mk
from shapely.geometry import box
import xarray as xr

from spatial_trends_ppe import annual_series, compute_trends, country_mask, hatch_mask, normalize_grid, trend_at_cell


class TrendTests(unittest.TestCase):
    def test_known_positive_trend(self):
        years = np.arange(1961, 2024)
        slope, p, n = trend_at_cell(0.03 * years + 2, years)
        self.assertAlmostEqual(slope, 0.3, places=10)
        self.assertLess(p, 0.05)
        self.assertEqual(n, 63)

    def test_complete_series_matches_source_estimator(self):
        rng = np.random.default_rng(123)
        y = rng.normal(size=63) + np.arange(63) * 0.03
        slope, p, _ = trend_at_cell(y, np.arange(1961, 2024))
        reference = mk.original_test(y)
        self.assertAlmostEqual(slope, reference.slope * 10, places=12)
        self.assertAlmostEqual(p, reference.p, places=12)

    def test_missing_observations_retain_elapsed_years(self):
        years = np.arange(2000, 2010)
        y = 2.0 * (years - 2000)
        y[[2, 3, 4, 5]] = np.nan
        slope, _, n = trend_at_cell(y, years, min_valid=3)
        self.assertEqual(n, 6)
        self.assertAlmostEqual(slope, 20.0)

    def test_missing_values_match_source_on_regular_annual_axis(self):
        years = np.arange(1961, 2024)
        rng = np.random.default_rng(99)
        y = rng.normal(size=63) + np.arange(63) * 0.04
        y[[4, 5, 6, 20, 40]] = np.nan
        slope, p, _ = trend_at_cell(y, years)
        reference = mk.original_test(y)
        self.assertAlmostEqual(slope, reference.slope * 10, places=12)
        self.assertAlmostEqual(p, reference.p, places=12)

    def test_constant_series(self):
        self.assertEqual(trend_at_cell(np.ones(40), np.arange(40)), (0.0, 1.0, 40))

    def test_all_missing(self):
        slope, p, n = trend_at_cell(np.full(40, np.nan), np.arange(40))
        self.assertTrue(np.isnan(slope) and np.isnan(p))
        self.assertEqual(n, 0)

    def test_insufficient_samples(self):
        slope, p, n = trend_at_cell(np.arange(10), np.arange(10))
        self.assertTrue(np.isnan(slope) and np.isnan(p))
        self.assertEqual(n, 10)


class InputTests(unittest.TestCase):
    def array(self, freq="YS", periods=4):
        return xr.DataArray(np.ones((periods, 2, 2)), dims=("time", "lat", "lon"),
                            coords={"time": pd.date_range("2000-01-01", periods=periods, freq=freq),
                                    "lat": [-20, -10], "lon": [-60, -50]})

    def test_normalization_descending_latitude_and_360_longitude(self):
        a = self.array().assign_coords(lon=[300, 310]).sortby("lat", ascending=False)
        result = normalize_grid(a)
        np.testing.assert_array_equal(result.lat, [-20, -10])
        np.testing.assert_array_equal(result.lon, [-60, -50])

    def test_duplicate_seam_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate lon"):
            normalize_grid(self.array().assign_coords(lon=[0, 360]))

    def test_monthly_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "one sample per year"):
            annual_series(self.array(freq="MS", periods=48), 2000, 2003, [-75, -30, -35, 10])

    def test_missing_year_rejected(self):
        with self.assertRaisesRegex(ValueError, "one sample per year"):
            annual_series(self.array().isel(time=[0, 2, 3]), 2000, 2003, [-75, -30, -35, 10])

    def test_netcdf_result_contains_full_pvalues_and_counts(self):
        result = compute_trends(self.array(), 3, 0.05, "degC")
        np.testing.assert_array_equal(result.trends, np.zeros((2, 2)))
        np.testing.assert_array_equal(result.pvalues, np.ones((2, 2)))
        np.testing.assert_array_equal(result.n_valid, np.full((2, 2), 4))

    def test_country_grid_centers(self):
        a = self.array().isel(time=0)
        country = gpd.GeoDataFrame(geometry=[box(-61, -21, -59, -19)], crs="EPSG:4326")
        np.testing.assert_array_equal(country_mask(a, country), [[True, False], [False, False]])


class PValueTests(unittest.TestCase):
    def test_raw_significant_missing_not_assumed_significant(self):
        p = np.array([0.01, 0.05, 0.3, np.nan])
        np.testing.assert_array_equal(hatch_mask(p, 0.05, "raw", "significant"), [True, True, False, False])

    def test_raw_nonsignificant(self):
        p = np.array([0.01, 0.05, 0.3, np.nan])
        np.testing.assert_array_equal(hatch_mask(p, 0.05, "raw", "nonsignificant"), [False, False, True, False])

    def test_legacy_significance_cannot_be_recovered(self):
        with self.assertRaisesRegex(ValueError, "Legacy files"):
            hatch_mask(np.array([np.nan, 0.3]), 0.05, "legacy-nonsignificant", "significant")

    def test_legacy_nonsignificant(self):
        np.testing.assert_array_equal(hatch_mask(np.array([np.nan, 0.3]), 0.05, "legacy-nonsignificant", "nonsignificant"), [False, True])

    def test_invalid_pvalues_rejected(self):
        with self.assertRaisesRegex(ValueError, "within"):
            hatch_mask(np.array([1.2]), 0.05, "raw", "nonsignificant")

    def test_mislabelled_legacy_file_rejected(self):
        with self.assertRaisesRegex(ValueError, "only retain"):
            hatch_mask(np.array([0.01, 0.3]), 0.05, "legacy-nonsignificant", "nonsignificant")


if __name__ == "__main__":
    unittest.main()
