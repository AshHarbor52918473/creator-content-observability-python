import unittest

from content_delivery import AssetJob, should_publish


class DeliveryDecisionTest(unittest.TestCase):
    def test_processed_asset_with_subscribers_is_published(self) -> None:
        job = AssetJob("creator-17", "video-204", 42, True)
        self.assertTrue(should_publish(job, new_processing_path=True))

    def test_unprocessed_asset_is_held(self) -> None:
        job = AssetJob("creator-17", "video-204", 42, False)
        self.assertFalse(should_publish(job, new_processing_path=True))


if __name__ == "__main__":
    unittest.main()

