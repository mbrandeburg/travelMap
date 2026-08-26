"""addTrip: matching, appends, and errors that no longer kill the process."""
import pytest

import mapBuilder


def _years(df, code):
    return mapBuilder.parse_years(df[df["Code"] == code].iloc[0]["Year Went"])


def test_exact_match_appends_and_updates_count(tracker):
    df = mapBuilder.addTrip("Japan", 2030)
    row = df[df["Code"] == "JPN"].iloc[0]
    assert "2030" in _years(df, "JPN")
    assert row["Have Been"] == len(_years(df, "JPN"))


def test_duplicate_year_is_allowed(tracker):
    before = len(_years(mapBuilder._load_df(), "JPN"))
    mapBuilder.addTrip("Japan", 2014)
    after = len(_years(mapBuilder._load_df(), "JPN"))
    assert after == before + 1


def test_fuzzy_match_resolves_typo(tracker):
    df = mapBuilder.addTrip("Braziil", 2031)  # typo -> Brazil
    assert "2031" in _years(df, "BRA")


def test_ambiguous_country_raises(tracker):
    with pytest.raises(mapBuilder.AmbiguousCountryError):
        mapBuilder.addTrip("Korea", 2032)  # matches North and South


def test_unknown_country_raises(tracker):
    with pytest.raises(mapBuilder.CountryNotFoundError):
        mapBuilder.addTrip("Zzzqqx", 2033)


def test_addtrip_persists_and_invalidates_cache(tracker):
    mapBuilder.addTrip("Canada", 2035)
    reloaded = mapBuilder._get_cached_dataframe()
    assert "2035" in _years(reloaded, "CAN")
