from dataclasses import dataclass
from datetime import datetime, timezone

from infrai_client import infrai


@dataclass(frozen=True)
class PaymentEvent:
    order_id: str
    due_at: datetime
    amount_cents: int
    risk_score: int


def notification_for(event: PaymentEvent) -> dict:
    level = "review" if event.risk_score >= 70 else "send"
    return {
        "event_id": event.order_id,
        "order_id": event.order_id,
        "due_at": event.due_at.astimezone(timezone.utc).isoformat(),
        "amount_cents": event.amount_cents,
        "action": level,
    }


def schedule_reminder(event: PaymentEvent, webhook_url: str) -> str:
    """Schedule a checkout reminder and queue the audit notification."""
    job = infrai.cron.create(cron_expr="0 9 * * *", task=webhook_url)
    infrai.queue.publish(queue="payment-reminders", payload=notification_for(event))
    return job["job_id"]


if __name__ == "__main__":
    sample = PaymentEvent(
        order_id="order-1042",
        due_at=datetime(2026, 9, 12, 9, tzinfo=timezone.utc),
        amount_cents=12900,
        risk_score=82,
    )
    print(schedule_reminder(sample, "https://shop.example/reminders/payment"))
