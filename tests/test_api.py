import sys
from pathlib import Path

# ensure repo root is on sys.path for imports during pytest collection
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_list_empty():
    resp = client.get("/entries")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# Note: these tests use an in-memory or local CouchDB instance; they may fail if CouchDB isn't running.
