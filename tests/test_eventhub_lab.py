"""Local checks: uv run --with azure-functions --with pytest python -m pytest tests/test_eventhub_lab.py."""

import datetime
import logging
import re

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


def test_message_schema_when_normal_batch_is_processed(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Given a batch with enqueue and sequence metadata.
    enqueued = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=30)
    events = [func.EventHubEvent(body=b"event", sequence_number=42, enqueued_time=enqueued)]

    # When the handler emits normal batch telemetry.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then the machine-parsed message exposes distinct age and duration fields.
    assert len(caplog.records) == 1
    match = re.fullmatch(
        r"EventHubBatch partition=unknown batchSize=1 seqRange=\[42-42\] "
        r"enqueueAgeSec=(\d+\.\d) processingMs=(\d+\.\d) delayMs=0",
        caplog.records[0].getMessage(),
    )
    assert match is not None
    dimensions = vars(caplog.records[0])["custom_dimensions"]
    assert float(match[1]) == dimensions["EnqueueAgeSeconds"]
    assert float(match[2]) == dimensions["ProcessingMs"]


def test_batch_telemetry_disabled_when_legacy_setting_is_false(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given disabled detailed telemetry and a batch that still earns a completion log.
    monkeypatch.setenv("EventHubLab__LogCheckpointDelta", "false")
    events = [func.EventHubEvent(body=b"event", sequence_number=i) for i in range(50)]

    # When the handler processes the batch.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then detailed telemetry is suppressed without suppressing batch completion.
    assert len(caplog.records) == 1
    assert caplog.records[0].getMessage().startswith("Batch completed:")
    assert "custom_dimensions" not in vars(caplog.records[0])


def test_artificial_delay_when_configured_is_applied_and_reported_separately(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given nonzero delay with simulated clocks and sleep, avoiding real waiting.
    monkeypatch.setenv("EventHubLab__ArtificialDelayMs", "250")
    sleeps: list[float] = []
    monkeypatch.setattr(eventhub_lab.time, "sleep", sleeps.append)
    ticks = iter([10.0, 10.375])
    monkeypatch.setattr(eventhub_lab.time, "monotonic", lambda: next(ticks))
    events = [func.EventHubEvent(body=b"event", sequence_number=42)]

    # When the handler processes the batch with artificial delay.
    with caplog.at_level(logging.INFO, logger=eventhub_lab.__name__):
        eventhub_lab.eventhub_lag_processor.build().get_user_function()(events)

    # Then configured milliseconds convert to sleep seconds, not lag or measured duration.
    assert sleeps == [0.25]
    assert len(caplog.records) == 1
    dimensions = vars(caplog.records[0])["custom_dimensions"]
    assert dimensions["ArtificialDelayMs"] == 250
    assert dimensions["ProcessingMs"] == 375.0
    assert dimensions["EnqueueAgeSeconds"] is None
    assert "CheckpointLagEvents" not in dimensions
