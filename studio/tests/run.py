from __future__ import annotations

import unittest


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("studio/tests", pattern="test_*.py")
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
