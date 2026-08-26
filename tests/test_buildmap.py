"""Map figure construction and data integrity."""
import pandas as pd
import plotly.graph_objects as go

import config
import mapBuilder


def test_buildmap_returns_figure_and_weight(tracker):
    fig, df = mapBuilder.buildMap()
    assert isinstance(fig, go.Figure)
    assert "Visit Weight" in df.columns
    # USA ('Home') must be pinned to the darkest shade → the max weight.
    usa_weight = df[df["Code"] == "USA"]["Visit Weight"].iloc[0]
    assert usa_weight == df["Visit Weight"].max()


def test_visited_rows_exclude_usa_and_sort(tracker):
    rows = mapBuilder.visited_rows(mapBuilder._get_cached_dataframe())
    assert all(r["country"] != "United States of America" for r in rows)
    assert [r["country"] for r in rows] == sorted(r["country"] for r in rows)
    spain = next(r for r in rows if r["country"] == "Spain")
    assert spain["latest"] == 2024


def test_tracker_codes_are_valid_iso_codes():
    valid = set(pd.read_csv(config.COUNTRY_CODES_PATH)["Code"])
    tracker = pd.read_csv(config.BASE_DIR / "Travel Tracker - Main.csv")
    assert set(tracker["Code"]).issubset(valid)


def test_empty_scaffold_is_all_unvisited(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_PATH", tmp_path / "fresh.csv")
    mapBuilder.invalidate_cache()
    df = mapBuilder.build_empty_tracker()
    assert (df["Have Been"] == 0).all()
    assert df.loc[df["Code"] == "USA", "Year Went"].iloc[0] == "Home"
