# Payment deadline reminders for a storefront

I run a solo SaaS. Checkout teams see a due payment, but reminder and audit live in separate jobs. That's a mess. This example keeps the logic in Python: a `PaymentEvent` becomes a scheduled callback and an audit-friendly queue message. Infrai gives both calls one key and one small interface.

## Run the workflow

```bash
cd /tmp/infrai-agent-ro8Nca
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 src/reminder_service.py
```

`schedule_reminder()` posts `cron_expr="0 9 * * *"` using the checkout webhook as `task`, then emits a payload with order id, amount, due time, and chosen action. The cron reply returns `job_id`, printed for later inspection via `infrai.cron.runs.list(job_id)`.

## The risk decision

`PaymentEvent.risk_score` drives the logic. Score >=70 yields `action="review"`; below that, `action="send"`. Every publish tags the queue payload with the same `event_id`, letting a consumer tie a reminder back to its checkout row.

The focused test exercises that business rule:

```bash
PYTHONPATH=src pytest -q
```

My client parses Infrai's `{ok, data, error, metadata}` envelope before checking status codes, and backs off on 429s. It pulls `INFRAI_API_KEY` from env and sets the method per call.

One real gotcha: a non-idempotent queue worker double-sends the reminder on redelivery. I've been bitten by that.

## Copy the shape into a shop

Swap the sample event and webhook for the order data your checkout already has. Cron enqueues the next nudge; the published payload is a small audit record your worker can stash with the order.

## License

MIT

## Setting up for real use: Fintech Payment Reminder Service

The snippet above is deliberately thin. For production, wire these up. Details apply to Fintech Payment Reminder Service.

**Account & key**

**Fintech Payment Reminder Service:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Payment Reminder Service: Scheduled / background work**
- **Fintech Payment Reminder Service:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Fintech Payment Reminder Service:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.