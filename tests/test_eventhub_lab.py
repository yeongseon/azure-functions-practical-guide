"""Local checks: uv run --with azure-functions --with pytest python -m pytest tests/test_eventhub_lab.py."""

import datetime
import logging

import azure.functions as func
import pytest

from apps.python.blueprints import eventhub_lab


@pytest.fixture(autouse=True)
def lab_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EventHubLab__ArtificialDelayMs", "0")
    monkeypatch.setenv("EventHubLab__LogCheckpointDelta", "true")


def test_checkpoint_lag_omitted_when_checkpoint_and_end_positions_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Given a real SDK event with batch metadata but no durable checkpoint/end position.
    events = [func.EventHubEvent(body=b"event", sequence_number=42)]

    # When the registered handler processes the batch locally.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then absence of a lag signal must not become a numeric zero claim.
    assert len(caplog.records) == 1
    assert "CheckpointLagEvents" not in vars(caplog.records[0])["custom_dimensions"]


def test_batch_measurements_remain_distinct_when_events_have_metadata(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given fixed clocks and deliberately distinct sequence, age and duration values.
    now = datetime.datetime(2026, 4, 7, 13, 30, tzinfo=datetime.timezone.utc)

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz: datetime.tzinfo | None = None) -> datetime.datetime:
            return now

    monkeypatch.setattr(datetime, "datetime", FixedDateTime)
    ticks = iter([10.0, 10.125])
    monkeypatch.setattr(eventhub_lab.time, "monotonic", lambda: next(ticks))
    events = [
        func.EventHubEvent(body=b"one", sequence_number=42, enqueued_time=now - datetime.timedelta(seconds=30)),
        func.EventHubEvent(body=b"two", sequence_number=44, enqueued_time=now - datetime.timedelta(seconds=10)),
    ]

    # When the handler logs the completed batch.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then the sequence range is not a count, duration is ms, and enqueue age is seconds.
    assert vars(caplog.records[0])["custom_dimensions"] == {
        "PartitionId": "unknown",
        "BatchSize": 2,
        "MinSequenceNumber": 42,
        "MaxSequenceNumber": 44,
        "EnqueueAgeSeconds": 30.0,
        "ProcessingMs": 125.0,
        "ArtificialDelayMs": 0,
    }


def test_enqueue_age_unknown_when_enqueue_timestamp_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Given a batch without enqueue timestamps.
    events = [func.EventHubEvent(body=b"event", sequence_number=0)]

    # When batch telemetry is emitted.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then missing age is explicitly unmeasured, not fabricated as zero seconds.
    assert vars(caplog.records[0])["custom_dimensions"]["EnqueueAgeSeconds"] is None
    assert "enqueueAgeSec=not-measured" in caplog.records[0].getMessage()


@pytest.mark.parametrize("events", [[], [func.EventHubEvent(body=b"event")]])
def test_lag_not_emitted_when_batch_or_sequence_metadata_missing(
    caplog: pytest.LogCaptureFixture, events: list[func.EventHubEvent],
) -> None:
    # Given an empty batch or an event without sequence metadata.
    # When the handler processes it.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then missing metadata must not manufacture a lag measurement.
    assert caplog.records == []
