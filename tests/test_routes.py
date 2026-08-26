"""Flask routes, including the regressions that used to crash the worker."""
import io

import mapBuilder


def test_index_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Countries Visited" in resp.data


def test_background_requires_country(client):
    resp = client.post("/background_process", data={"data": "", "data2": ""})
    assert resp.status_code == 400


def test_background_adds_trip(client):
    resp = client.post("/background_process", data={"data": "Japan", "data2": "2040"})
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_background_ambiguous_is_400_not_crash(client):
    resp = client.post("/background_process", data={"data": "Korea", "data2": "2041"})
    assert resp.status_code == 400
    assert "options" in resp.get_json()


def test_background_unknown_is_400(client):
    resp = client.post("/background_process", data={"data": "Zzzqqx", "data2": ""})
    assert resp.status_code == 400


def test_upload_rejects_non_csv(client):
    data = {"file": (io.BytesIO(b"hello"), "notes.txt")}
    resp = client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 302  # bounced back with a flash message


def test_upload_rejects_missing_columns(client):
    data = {"file": (io.BytesIO(b"foo,bar\n1,2\n"), "bad.csv")}
    resp = client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 302


def test_upload_valid_updates_data_and_invalidates_cache(client):
    good = (
        b"Code,Country,Have Been,Year Went\n"
        b"JPN,Japan,1,[2099]\n"
        b"USA,United States of America,0,Home\n"
    )
    data = {"file": (io.BytesIO(good), "good.csv")}
    resp = client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 302
    df = mapBuilder._get_cached_dataframe()
    assert "2099" in mapBuilder.parse_years(df[df["Code"] == "JPN"].iloc[0]["Year Went"])
