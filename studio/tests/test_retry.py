from __future__ import annotations

import unittest

from studio.core.jobs import JobQueue


class RetryTests(unittest.TestCase):
    def test_retry_playbook_applies_once_then_stops_on_same_tag(self):
        q = JobQueue(max_retries_per_failure=2)
        should_retry, recipe = q.retry_plan("cheap_vfx")
        self.assertTrue(should_retry)
        self.assertIn("rim light", recipe)
        should_retry, reason = q.retry_plan("cheap_vfx")
        self.assertFalse(should_retry)
        self.assertIn("human review", reason)
        should_retry, reason = q.retry_plan("unknown_tag")
        self.assertFalse(should_retry)
        self.assertIn("no retry playbook", reason)

    def test_retry_prompt_records_prompt_diff(self):
        q = JobQueue(max_retries_per_failure=2)
        should_retry, prompt, diff = q.retry_prompt("base prompt", "product_dull")
        self.assertTrue(should_retry)
        self.assertIn("base prompt", prompt)
        self.assertIn("Retry adjustment for product_dull", diff)


if __name__ == "__main__":
    unittest.main()
