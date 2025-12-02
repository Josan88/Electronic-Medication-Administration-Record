"""Tests for hybrid service fallback behavior when local data is missing."""

import pytest

from services.hybrid_service import HybridDataServiceError, hybrid_service
from services.thingspeak_service import ThingSpeakError


def test_read_channel_falls_back_to_thingspeak(monkeypatch):
    """Ensure ThingSpeak is used when local storage has no records."""
    channel_name = "medicine_track"
    remote_data = [
        {
            "patient_id": "PX001",
            "medicine_name": "TestMed",
            "consume_date": "2025-11-13 10:00:00",
            "time_slot": "10:00",
        }
    ]

    monkeypatch.setattr(hybrid_service.local_db, "read_channel", lambda name: [])

    ts_calls = []

    def fake_read_channel(name):
        ts_calls.append(name)
        return remote_data

    monkeypatch.setattr(
        hybrid_service.thingspeak_service, "read_channel", fake_read_channel
    )

    result = hybrid_service.read_channel(channel_name)

    assert result == remote_data
    assert ts_calls == [channel_name]


def test_medicine_track_prefers_local_when_available(monkeypatch):
    """Medicine track reads should come from local DB when data is available (changed behavior)."""
    channel_name = "medicine_track"
    local_data = [
        {"patient_id": "PX010", "medicine_name": "LocalMed", "time_slot": "09:00"}
    ]
    remote_calls = []

    monkeypatch.setattr(
        hybrid_service.local_db,
        "read_channel",
        lambda name: local_data,
    )
    monkeypatch.setattr(
        hybrid_service.thingspeak_service,
        "read_channel",
        lambda name: (remote_calls.append(name)) or [{"patient_id": "REMOTE"}],
    )

    result = hybrid_service.read_channel(channel_name)

    assert result == local_data
    assert remote_calls == []  # ThingSpeak should not be called when local has data


def test_medicine_track_falls_back_to_thingspeak_when_local_empty(monkeypatch):
    """If local DB has no data, medicine_track read should fall back to ThingSpeak."""
    channel_name = "medicine_track"
    remote_data = [{"patient_id": "PX011", "time_slot": "13:00"}]

    monkeypatch.setattr(hybrid_service.local_db, "read_channel", lambda name: [])
    monkeypatch.setattr(
        hybrid_service.thingspeak_service, "read_channel", lambda name: remote_data
    )

    result = hybrid_service.read_channel(channel_name)

    assert result == remote_data


def test_find_by_field_falls_back_to_thingspeak(monkeypatch):
    """Fallback search should hit ThingSpeak when local results are empty."""
    channel_name = "patient_info"
    expected = [{"patient_id": "PX002", "name": "Alice"}]

    monkeypatch.setattr(hybrid_service.local_db, "find_by_field", lambda c, f, v: [])

    ts_calls = []

    def fake_find_by_field(c, f, v):
        ts_calls.append((c, f, v))
        return expected

    monkeypatch.setattr(
        hybrid_service.thingspeak_service, "find_by_field", fake_find_by_field
    )

    result = hybrid_service.find_by_field(channel_name, "patient_id", "PX002")

    assert result == expected
    assert ts_calls == [(channel_name, "patient_id", "PX002")]


def test_medicine_track_search_prefers_local_when_available(monkeypatch):
    """Medicine track searches should use local DB when data is available (changed behavior)."""
    channel_name = "medicine_track"
    local_data = [{"patient_id": "PX012", "time_slot": "21:00"}]
    remote_calls = []

    monkeypatch.setattr(
        hybrid_service.local_db,
        "find_by_field",
        lambda c, f, v: local_data,
    )
    monkeypatch.setattr(
        hybrid_service.thingspeak_service,
        "find_by_field",
        lambda c, f, v: (remote_calls.append((c, f, v))) or [{"patient_id": "REMOTE"}],
    )

    result = hybrid_service.find_by_field(channel_name, "patient_id", "PX012")

    assert result == local_data
    assert remote_calls == []  # ThingSpeak should not be called when local has data


def test_medicine_track_search_errors_when_thingspeak_unavailable(monkeypatch):
    """ThingSpeak search failure for medicine_track should raise (no local fallback)."""
    channel_name = "medicine_track"

    def fail_find_by_field(c, f, v):
        raise ThingSpeakError("remote search down")

    monkeypatch.setattr(
        hybrid_service.thingspeak_service, "find_by_field", fail_find_by_field
    )

    with pytest.raises(HybridDataServiceError):
        hybrid_service.find_by_field(channel_name, "patient_id", "PX013")
