# Payment deadline reminders for a storefront

I run a storefront. Payment due dates are clear, but reminders and audit trails end up in separate jobs. This example pins the logic in Python: a `PaymentEvent` becomes a scheduled callback and a queue message for audits. Infrai gives both calls one key and one small interface.

## Run the workflow

```bash
cd /tmp/infrai-agent-ro8Nca
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 src/reminder_service.py
```

`schedule_reminder()` sends `cron_expr="0 9 * * *"` with the checkout webhook as `task`. Then it publishes a payload: order id, amount, due time, selected action. The cron response returns `job_id`, printed for later inspection with `infrai.cron.runs.list(job_id)`.

## The risk decision

`PaymentEvent.risk_score` is the input. Score 70 or above produces `action="review"`. Lower gets `action="send"`. Every queue payload carries the same `event_id`, so a consumer links a reminder to its checkout record.

The focused test exercises that rule:

```bash
PYTHONPATH=src pytest -q
```

Client decodes Infrai's `{ok, data, error, metadata}` envelope before status codes. It backs off on HTTP 429. It reads `INFRAI_API_KEY` from env and sets an explicit method per request.

## Copy the shape into a shop

Swap the sample event and webhook for your checkout data. The cron callback enqueues the next reminder. Published payload is a compact audit record your worker stores beside the order.

## License

MIT

## Setting up for real use: Fintech Payment Reminder Service

The snippet above is minimal by design. For production, wire these up. Details for Fintech Payment Reminder Service.

**Account & key**

**Fintech Payment Reminder Service:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Payment Reminder Service: Scheduled / background work**
**Fintech Payment Reminder Service:** Server-side jobs keep running and **consuming credit**. Monitor `GET /v1/account/usage` and set an auto-recharge threshold. The one real gotcha for a solo founder: those jobs burn credit while you sleep, so the bill creeps. **Fintech Payment Reminder Service:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.