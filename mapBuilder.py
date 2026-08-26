"""Map builder using Plotly.

Trip years are stored in the 'Year Went' column as a canonical bracketed list
(e.g. "['2019', '2022']") or the sentinels 'N/A' (never) and 'Home' (USA).
The tracker CSV at config.DATA_PATH is the single source of truth.
"""
import os
import re
import math
import contextlib
from functools import lru_cache

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from rapidfuzz import process, fuzz

import config


class CountryNotFoundError(ValueError):
    """Raised when a country name cannot be matched, even fuzzily."""


class AmbiguousCountryError(ValueError):
    """Raised when a country name matches more than one country."""

    def __init__(self, options):
        self.options = list(options)
        super().__init__(
            "More than one country matches; please be more specific: "
            + ", ".join(self.options)
        )


# ---- Year-list parsing -------------------------------------------------------

def parse_years(value):
    """Return a clean list of trip labels from a (possibly messy) 'Year Went' cell.

    Tolerates legacy shapes like "['2009','2016']", "[2011]", " 2016 ", real
    lists, plain strings, and the 'N/A'/'Home' sentinels.
    """
    if value is None:
        return []
    if isinstance(value, float) and math.isnan(value):
        return []
    if isinstance(value, (list, tuple)):
        raw = list(value)
    else:
        text = str(value).strip()
        if not text or text.lower() in ("n/a", "nan", "home"):
            return []
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        raw = text.split(",")
    labels = []
    for item in raw:
        label = str(item).strip().strip("'\"").strip()
        if label and label.lower() not in ("n/a", "nan"):
            labels.append(label)
    return labels


def _clean_label(label):
    """Normalise one trip label; commas are dropped so they can't corrupt the list."""
    text = str(label).strip().strip("[]'\"").strip()
    return re.sub(r"\s+", " ", text.replace(",", " ")).strip()


def format_years(years):
    """Serialise trip labels to the canonical cell format, or 'N/A' when empty."""
    if not years:
        return "N/A"
    return "[" + ", ".join(f"'{y}'" for y in years) + "]"


# ---- Storage -----------------------------------------------------------------

@contextlib.contextmanager
def _file_lock(path):
    """Best-effort exclusive lock so concurrent writers can't corrupt the CSV."""
    try:
        import fcntl
    except ImportError:  # pragma: no cover - non-POSIX fallback
        yield
        return
    with open(str(path) + ".lock", "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _write_df(df):
    """Atomically persist the tracker CSV under an exclusive lock."""
    path = config.DATA_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with _file_lock(path):
        tmp = path.with_name(path.name + ".tmp")
        df.to_csv(tmp, index=False)
        os.replace(tmp, path)


def build_empty_tracker():
    """Scaffold an all-unvisited tracker from the country list.

    Fallback only: the live CSV (config.DATA_PATH) is the source of truth once
    it exists, so this just supplies a blank template when none is present.
    """
    df = pd.read_csv(config.COUNTRY_CODES_PATH)
    df["Have Been"] = 0
    df["Year Went"] = "N/A"
    df.loc[df["Code"] == "USA", "Year Went"] = "Home"
    _write_df(df)
    return df


def _load_df():
    """Read the tracker CSV, scaffolding an empty one only if it does not exist."""
    if config.DATA_PATH.exists():
        df = pd.read_csv(config.DATA_PATH)
        df["Year Went"] = df["Year Went"].fillna("N/A")
        return df
    return build_empty_tracker()


@lru_cache(maxsize=1)
def _get_cached_dataframe():
    return _load_df()


def invalidate_cache():
    """Drop the cached frame; call after any write or upload."""
    _get_cached_dataframe.cache_clear()


# ---- Trips -------------------------------------------------------------------

def _match_country(countries, query):
    """Resolve a user-supplied name to exactly one country, else raise."""
    needle = str(query).strip().lower()
    matches = [c for c in countries if needle in c.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise AmbiguousCountryError(matches)
    best = process.extractOne(query, list(countries), scorer=fuzz.WRatio)
    if best and best[1] >= config.FUZZY_MATCH_THRESHOLD:
        return best[0]
    raise CountryNotFoundError(
        f"'{query}' was not recognised."
        + (f" Closest match: {best[0]}." if best else "")
    )


def _apply_trip(df, country, year_went):
    """Append one trip to the matching country row (in place) and update the count."""
    target = _match_country(df["Country"].tolist(), country)
    idx = df.index[df["Country"] == target][0]
    years = parse_years(df.at[idx, "Year Went"])
    years.append(_clean_label(year_went))
    df.at[idx, "Year Went"] = format_years(years)
    df.at[idx, "Have Been"] = len(years)
    return df


def addTrip(country, yearWent):
    """Add a trip to the persistent tracker and return the updated frame.

    Raises AmbiguousCountryError / CountryNotFoundError instead of exiting, so a
    bad web request becomes a 400 rather than killing the worker process.
    """
    df = _load_df()
    _apply_trip(df, country, yearWent)
    _write_df(df)
    invalidate_cache()
    return df


# ---- Rendering ---------------------------------------------------------------

_COLORSCALE = [
    [0.0, "rgb(247, 247, 247)"],   # unvisited
    [0.1, "rgb(220, 245, 235)"],
    [0.3, "rgb(180, 217, 204)"],
    [0.5, "rgb(137, 192, 182)"],
    [0.7, "rgb(99, 166, 160)"],
    [0.85, "rgb(68, 140, 138)"],
    [1.0, "rgb(13, 88, 95)"],      # most visited / home
]


def _is_home(series):
    return series.astype(str).str.strip().str.lower() == "home"


def visited_rows(df):
    """Rows for the list/table view: visited countries with their trip labels.

    'latest' is the most recent 4-digit year found (0 if none); it is the numeric
    sort key for the Years column, since labels can be free text.
    """
    rows = []
    for _, row in df.iterrows():
        if row["Code"] == "USA":
            continue
        years = parse_years(row["Year Went"])
        if years:
            found = [int(y) for label in years for y in re.findall(r"\d{4}", str(label))]
            rows.append(
                {
                    "country": row["Country"],
                    "count": len(years),
                    "years": ", ".join(years),
                    "latest": max(found) if found else 0,
                }
            )
    rows.sort(key=lambda r: r["country"])
    return rows


def buildMap():
    df = _get_cached_dataframe().copy()
    df["Year Went"] = df["Year Went"].fillna("N/A")

    years_lists = df["Year Went"].apply(parse_years)
    counts = years_lists.apply(len)
    is_home = _is_home(df["Year Went"])
    max_count = int(counts.max()) if len(counts) else 0
    home_weight = max_count + 1 if max_count > 0 else 1

    # Colour by true trip count; 'Home' (USA) is pinned to the darkest shade.
    df["Visit Weight"] = counts.where(~is_home, home_weight)

    hover = []
    for (_, row), years in zip(df.iterrows(), years_lists):
        if str(row["Year Went"]).strip().lower() == "home":
            detail = "Home"
        elif years:
            detail = ", ".join(years)
        else:
            detail = "Never visited"
        hover.append(
            f"<b>{row['Country']}</b><br>Trips: {len(years)}<br>Years: {detail}<extra></extra>"
        )
    df["Hover Text"] = hover

    fig = go.Figure(
        data=go.Choropleth(
            locations=df["Code"],
            z=df["Visit Weight"],
            text=df["Country"],
            hovertemplate=df["Hover Text"],
            zmin=0,
            zmax=home_weight,
            colorscale=_COLORSCALE,
            marker_line_color="rgb(204, 204, 204)",
            marker_line_width=0.4,
            colorbar=dict(
                title="Trips",
                orientation="h",
                y=-0.12,
                thickness=14,
                len=0.6,
                tickmode="array",
                tickvals=list(range(0, home_weight + 1)),
                ticktext=[str(i) for i in range(0, max_count + 1)] + ["Home"],
            ),
        )
    )

    fig.update_layout(
        title={
            "text": "Places I've Been",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2c3e50"},
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgb(204, 204, 204)",
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(family="Inter, Arial, Helvetica, sans-serif", size=13, color="#2c3e50"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        autosize=True,
        dragmode="pan",
    )

    return fig, df
