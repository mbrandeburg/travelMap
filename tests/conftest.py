"""Shared pytest fixtures: point the app at a temp copy of the tracker CSV."""
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def tracker(tmp_path, monkeypatch):
    """Copy the real tracker to a temp path and route the app at it."""
    import config
    import mapBuilder

    data = tmp_path / "Travel Tracker - Main.csv"
    shutil.copy(REPO_ROOT / "Travel Tracker - Main.csv", data)
    monkeypatch.setattr(config, "DATA_PATH", data)
    mapBuilder.invalidate_cache()
    yield data
    mapBuilder.invalidate_cache()


@pytest.fixture
def client(tracker):
    import runApp

    runApp.app.config.update(TESTING=True)
    return runApp.app.test_client()
