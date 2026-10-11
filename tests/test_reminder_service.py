from datetime import datetime, timezone

from reminder_service import PaymentEvent, notification_for, schedule_reminder


def test_high_risk_payment_requires_review():
    event = PaymentEvent("order-7", datetime(2026, 9, 12, tzinfo=timezone.utc), 5000, 70)
    result = notification_for(event)
    assert result["action"] == "review"
    assert result["event_id"] == "order-7"


def test_schedule_reminder_publishes_to_payment_reminders(monkeypatch):
    event = PaymentEvent("order-7", datetime(2026, 9, 12, tzinfo=timezone.utc), 5000, 70)
    published = {}

    monkeypatch.setattr(
        "reminder_service.infrai.cron.create",
        lambda **kwargs: {"job_id": "job-1"},
    )
    monkeypatch.setattr(
        "reminder_service.infrai.queue.publish",
        lambda **kwargs: published.update(kwargs),
    )

    assert schedule_reminder(event, "https://shop.example/reminders/payment") == "job-1"
    assert published == {"queue": "payment-reminders", "payload": notification_for(event)}
