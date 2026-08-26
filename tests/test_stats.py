"""calculate_stats: robust trip/country/year counting, USA excluded."""
import pandas as pd

import runApp


def _df():
    return pd.DataFrame(
        {
            "Code": ["USA", "GRC", "AND", "AFG"],
            "Country": [
                "United States of America",
                "Greece",
                "Andorra",
                "Afghanistan",
            ],
            "Have Been": [15, 2, 1, 0],
            "Year Went": ["Home", "['2009','2016']", "[2011]", "N/A"],
        }
    )


def test_counts_exclude_usa_and_handle_no_space_delimiter():
    stats = runApp.calculate_stats(_df())
    assert stats["countries"] == 2          # Greece + Andorra
    assert stats["trips"] == 3              # 2 (Greece) + 1 (Andorra)
    assert stats["years"] == 2016 - 2009 + 1


def test_empty_frame_is_all_zero():
    empty = pd.DataFrame(
        {"Code": ["AFG"], "Country": ["Afghanistan"], "Have Been": [0], "Year Went": ["N/A"]}
    )
    assert runApp.calculate_stats(empty) == {"countries": 0, "trips": 0, "years": 0}


def test_non_numeric_labels_counted_as_trips_but_years_extracted():
    df = pd.DataFrame(
        {
            "Code": ["ESP"],
            "Country": ["Spain"],
            "Have Been": [2],
            "Year Went": ["['Study Abroad 2011-2012', 2024]"],
        }
    )
    stats = runApp.calculate_stats(df)
    assert stats["trips"] == 2
    assert stats["years"] == 2024 - 2011 + 1
