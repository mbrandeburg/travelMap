"""Year-list parsing/formatting — the source of the old trip-count bugs."""
import numpy as np
import pytest

import mapBuilder


@pytest.mark.parametrize(
    "value,expected",
    [
        ("N/A", []),
        ("Home", []),
        (None, []),
        ("[2011]", ["2011"]),
        ("['2021', 2023]", ["2021", "2023"]),
        ("['2010', ' 2016', 2018]", ["2010", "2016", "2018"]),
        # No space after the comma — the case that undercounted Greece before.
        ("['2009','2016']", ["2009", "2016"]),
        (
            "['Study Abroad 2011-2012', '  2017', ' 2023', 2024]",
            ["Study Abroad 2011-2012", "2017", "2023", "2024"],
        ),
        (["2012", 2013], ["2012", "2013"]),
    ],
)
def test_parse_years(value, expected):
    assert mapBuilder.parse_years(value) == expected


def test_parse_years_nan():
    assert mapBuilder.parse_years(np.nan) == []


def test_format_years_round_trip():
    assert mapBuilder.format_years(["2011", "2016"]) == "['2011', '2016']"
    assert mapBuilder.parse_years(mapBuilder.format_years(["2011", "2016"])) == ["2011", "2016"]
    assert mapBuilder.format_years([]) == "N/A"


def test_clean_label_strips_and_dedupes_whitespace():
    assert mapBuilder._clean_label(2011) == "2011"
    assert mapBuilder._clean_label("  2016 ") == "2016"
    # Commas are removed so a label can never corrupt the stored list.
    assert "," not in mapBuilder._clean_label("Dec 2020, Jan 2021")
