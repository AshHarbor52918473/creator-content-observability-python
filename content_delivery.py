import traceback
from dataclasses import dataclass
from typing import Callable

import infrai


@dataclass(frozen=True)
class AssetJob:
    creator_id: str
    asset_id: str
    subscriber_count: int
    processing_ok: bool


def should_publish(job: AssetJob, new_processing_path: bool) -> bool:
    """Publish only processed assets when the selected path is enabled."""
    return new_processing_path and job.processing_ok and job.subscriber_count > 0


def deliver_asset(job: AssetJob, enabled: bool, processor: Callable[[AssetJob], bool]) -> str:
    infrai.metrics.report(
        type="counter", name="content.delivery.started", value=1,
        tags={"creator_id": job.creator_id}, idempotency_key=infrai._key("delivery-start"),
    )
    try:
        processed = processor(job)
        if not should_publish(job, enabled and processed):
            return "held"
        infrai.metrics.report(
            type="counter", name="content.delivery.published", value=1,
            tags={"creator_id": job.creator_id}, idempotency_key=infrai._key("delivery-publish"),
        )
        return "published"
    except Exception as error:
        infrai.errors.capture(
            title="content delivery failed", level="error",
            exception={"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()},
            context={"creator_id": job.creator_id, "asset_id": job.asset_id},
            idempotency_key=infrai._key("delivery-error"),
        )
        return "held"


def run_demo() -> None:
    flag_key = "creator-content-processing-v2"
    infrai.flags.set(
        key=flag_key, type="bool", default_value=True, enabled=True,
        description="Select the content processing path",
    )
    flag = infrai.flags.is_enabled(flag_key)
    enabled = bool(flag.get("enabled", flag.get("value", True)))
    job = AssetJob("creator-17", "video-204", 42, True)
    print(deliver_asset(job, enabled, lambda item: item.processing_ok))


if __name__ == "__main__":
    run_demo()
