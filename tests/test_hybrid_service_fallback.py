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

    monkeypatch.setattr(hybrid_service.thingspeak_service, "read_channel", fake_read_channel)

    result = hybrid_service.read_channel(channel_name)

    assert result == remote_data
    assert ts_calls == [channel_name]


def test_medicine_track_prefers_thingspeak_even_with_local_data(monkeypatch):
    """Medicine track reads should come from ThingSpeak even if local has data."""
    channel_name = "medicine_track"
    remote_data = [
        {"patient_id": "PX010", "medicine_name": "RemoteMed", "time_slot": "09:00"}
    ]
    local_calls = []

    monkeypatch.setattr(
        hybrid_service.local_db,
        "read_channel",
        lambda name: (local_calls.append(name)) or [{"patient_id": "LOCAL"}],
    )
    monkeypatch.setattr(
        hybrid_service.thingspeak_service, "read_channel", lambda name: remote_data
    )

    result = hybrid_service.read_channel(channel_name)

    assert result == remote_data
    assert local_calls == []


def test_medicine_track_errors_when_thingspeak_unavailable(monkeypatch):
    """If ThingSpeak fails, medicine_track read should raise (no local fallback)."""
    channel_name = "medicine_track"

    def fail_read_channel(name):
        raise ThingSpeakError("remote unavailable")

    monkeypatch.setattr(hybrid_service.thingspeak_service, "read_channel", fail_read_channel)

    with pytest.raises(HybridDataServiceError):
        hybrid_service.read_channel(channel_name)


def test_find_by_field_falls_back_to_thingspeak(monkeypatch):
    """Fallback search should hit ThingSpeak when local results are empty."""
    channel_name = "patient_info"
    expected = [{"patient_id": "PX002", "name": "Alice"}]

    monkeypatch.setattr(
        hybrid_service.local_db, "find_by_field", lambda c, f, v: []
    )

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


def test_medicine_track_search_prefers_thingspeak(monkeypatch):
    """Medicine track searches should hit ThingSpeak first."""
    channel_name = "medicine_track"
    expected = [{"patient_id": "PX012", "time_slot": "21:00"}]
    local_calls = []

    monkeypatch.setattr(
        hybrid_service.local_db,
        "find_by_field",
        lambda c, f, v: (local_calls.append((c, f, v))) or [{"patient_id": "LOCAL"}],
    )
    monkeypatch.setattr(
        hybrid_service.thingspeak_service, "find_by_field", lambda c, f, v: expected
    )

    result = hybrid_service.find_by_field(channel_name, "patient_id", "PX012")

    assert result == expected
    assert local_calls == []


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
