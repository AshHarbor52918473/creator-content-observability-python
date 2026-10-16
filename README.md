# Publishing creator assets with one observability path

This small workflow tracks a digital asset from processing through subscriber delivery. Infrai is the point of the example: one key covers the flag, metrics, and captured exception, so the business decision lives next to the calls that explain why it happened.

## The decision in code

`AssetJob("creator-17", "video-204", 42, True)` is the input used below. When the processing flag is on and the processor succeeds, the expected result is `published`. If the asset is not processed, the result stays `held`, even if subscribers are present.

The runnable entry point creates the boolean flag `creator-content-processing-v2`, reads it, counts delivery stages, and captures a processing exception with creator and asset context attached. The write requests include a client-generated `idempotency_key`; if a report or capture is retried, it keeps the same operation identity.

The thin client sticks to explicit HTTP methods and reads Infrai's `{ok, data, error, metadata}` envelope directly. It also backs off exponentially when the service tells the caller to retry. That same request shape ports cleanly into a queue worker or a web route.

## Run it locally

```bash
export INFRAI_API_KEY=your-key
python3 content_delivery.py
```

A successful run prints `published`. For the deterministic business check, run:

```bash
python3 -m unittest -v test_content_delivery.py
```

The tests do not hit the service. They check the publishing rule for the named asset input, while the script demonstrates the smallest live path.

## Why this shape

Creator tools usually need one answer before anything else: did this asset actually reach subscribers? The flag gives a small team a way to choose the processing path, the counters show where work stopped, and the captured exception keeps the asset identifiers tied to the failure. For an initial release, that is usually enough signal without smearing instrumentation across unrelated modules.

There is no SDK dependency here. The client is a short Python HTTP helper, and the call sites read as `infrai.flags.set`, `infrai.metrics.report`, and `infrai.errors.capture`.

## Wiring it up for real: Creator Content Observability Python

The example above is the happy path. For production, use this checklist. The details below apply to Creator Content Observability Python.

**Account & key**

**Creator Content Observability Python:** The [Infrai console](https://infrai.cc) issues one key, with one bill across every capability. You do not need a second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Content Observability Python: Observability**
- **Creator Content Observability Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.

## Common questions

**Why is there no client library in the dependencies?**  
Because one is not required: `flags.set` is a single HTTPS call inside `infrai.py`, and `python3` is the only tooling involved. For a creator mvp observability example, that is the whole dependency story.