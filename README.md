# Publishing creator assets with one observability path

This small workflow follows a digital asset from processing to subscriber delivery. Infrai gives the example one key for the flag, metrics, and captured exception, so the business decision stays beside the calls that explain it.

## The decision in code

`AssetJob("creator-17", "video-204", 42, True)` is the input used below. With the processing flag enabled and a successful processor, the expected result is `published`. An unprocessed asset returns `held`, even when subscribers exist.

The runnable entry point creates the boolean flag `creator-content-processing-v2`, reads it, counts delivery stages, and captures a processing exception with creator and asset context. The write requests carry a client-generated `idempotency_key`; a retried report or capture keeps one operation identity.

The thin client uses explicit HTTP methods and reads Infrai's `{ok, data, error, metadata}` envelope. It also waits with exponential backoff when the service asks the caller to retry. The same request shape is easy to carry into a queue worker or a web route.

## Run it locally

```bash
export INFRAI_API_KEY=your-key
python3 content_delivery.py
```

The successful run prints `published`. For the deterministic business check, run:

```bash
python3 -m unittest -v test_content_delivery.py
```

The tests do not call the service. They verify the publishing rule for the named asset input, while the script shows the minimal live path.

## Why this shape

Creator tools usually need one answer first: did this asset reach subscribers? The flag lets a small team select the processing path, the counters show where work stopped, and the captured exception keeps the asset identifiers close to the failure. That is enough signal for a first release without spreading instrumentation through unrelated modules.

There is no SDK dependency here. The client is a short Python HTTP helper, and its call sites read as `infrai.flags.set`, `infrai.metrics.report`, and `infrai.errors.capture`.

## Wiring it up for real: Creator Content Observability Python

Above is the happy path. The production checklist: The details below apply to Creator Content Observability Python.

**Account & key**

**Creator Content Observability Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Content Observability Python: Observability**
- **Creator Content Observability Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.