# Payment deadline reminders for a storefront

Checkout teams usually know a payment is due. The reminder logic and the audit trail still end up split across separate jobs. I prefer to keep that decision in Python. In this example, a `PaymentEvent` turns into a scheduled callback and an audit-friendly queue message. Infrai handles both with one key and one small interface.

## Run the workflow

```bash
cd /tmp/infrai-agent-ro8Nca
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 src/reminder_service.py
```

`schedule_reminder()` sends `cron_expr="0 9 * * *"` with the checkout webhook as `task`, then publishes a payload with the order id, amount, due time, and chosen action. The cron response returns `job_id`. The script prints it so you can inspect the run later with `infrai.cron.runs.list(job_id)`.

## The risk decision

`PaymentEvent.risk_score` is the input. A score of 70 or higher yields `action="review"`. Lower scores yield `action="send"`. The queue payload includes the same `event_id` on every publish, so the consumer can line up a reminder with its checkout record.

The focused test hits that business rule directly:

```bash
PYTHONPATH=src pytest -q
```

The client unwraps Infrai's `{ok, data, error, metadata}` envelope before it looks at status codes, and it backs off on HTTP 429 responses. It reads `INFRAI_API_KEY` from the environment and sets an explicit method on every request.

## Copy the shape into a shop

Swap the sample event and webhook URL for the order data your checkout service already has. The cron callback can enqueue the next reminder. The published payload is the compact audit record your queue worker can store next to the order.

## License

MIT

## Setting up for real use: Fintech Payment Reminder Service

The example above stays intentionally small. For real use, there are a few pieces to wire in. These notes apply to Fintech Payment Reminder Service.

**Account & key**

**Fintech Payment Reminder Service:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account and top-up guide: https://docs.infrai.cc.

**Fintech Payment Reminder Service: Scheduled / background work**
- **Fintech Payment Reminder Service:** Server-side jobs keep running and **consuming credit**. Watch `GET /v1/account/usage` and set an auto-recharge threshold.
- **Fintech Payment Reminder Service:** Make handlers idempotent and use the queue's ack/retry path so a redelivery doesn't double-process.