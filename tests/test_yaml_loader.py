import os
import json
import datetime
import hashlib
import builtins

import pytest

from open_bus_pipelines import yaml_loader


class DummyResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")


def test_get_from_url_success(monkeypatch, tmp_path):
    url = "http://example.com/data"
    monkeypatch.setattr(yaml_loader, "CACHE_PATH", str(tmp_path))

    def fake_get(requested_url, timeout=15):
        assert requested_url == url
        return DummyResponse("hello")

    monkeypatch.setattr(yaml_loader.requests, "get", fake_get)

    result = yaml_loader.get_from_url(url)
    assert result == "hello"
    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cache_file = tmp_path / f"{cache_key}.json"
    assert cache_file.exists()
    data = json.loads(cache_file.read_text())
    assert data["text"] == "hello"


def _write_cache(tmp_path, url, text, delta_days):
    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cache_file = tmp_path / f"{cache_key}.json"
    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=delta_days)
    cache_file.write_text(json.dumps({
        "url": url,
        "datetime": dt.strftime('%Y-%m-%dT%H:%M:%S%z'),
        "text": text
    }))
    return cache_file


def test_get_from_url_use_cache(monkeypatch, tmp_path):
    url = "http://example.com/data"
    monkeypatch.setattr(yaml_loader, "CACHE_PATH", str(tmp_path))
    _write_cache(tmp_path, url, "cached", 2)

    def fake_get(*args, **kwargs):
        raise Exception("network error")

    monkeypatch.setattr(yaml_loader.requests, "get", fake_get)
    result = yaml_loader.get_from_url(url)
    assert result == "cached"


def test_get_from_url_cache_too_old(monkeypatch, tmp_path):
    url = "http://example.com/data"
    monkeypatch.setattr(yaml_loader, "CACHE_PATH", str(tmp_path))
    _write_cache(tmp_path, url, "old", 6)

    def fake_get(*args, **kwargs):
        raise Exception("network error")

    monkeypatch.setattr(yaml_loader.requests, "get", fake_get)
    with pytest.raises(Exception):
        yaml_loader.get_from_url(url)


def test_get_from_url_no_cache(monkeypatch, tmp_path):
    url = "http://example.com/data"
    monkeypatch.setattr(yaml_loader, "CACHE_PATH", str(tmp_path))

    def fake_get(*args, **kwargs):
        raise Exception("network error")

    monkeypatch.setattr(yaml_loader.requests, "get", fake_get)
    with pytest.raises(Exception):
        yaml_loader.get_from_url(url)


def test_yaml_safe_load_local(tmp_path):
    f = tmp_path / "file.yaml"
    f.write_text("a: 1")
    assert yaml_loader.yaml_safe_load(str(f)) == {"a": 1}


def test_yaml_safe_load_url(monkeypatch):
    url = "http://example.com/data.yaml"
    monkeypatch.setattr(yaml_loader, "get_from_url", lambda u: "b: 2")
    assert yaml_loader.yaml_safe_load(url) == {"b": 2}
