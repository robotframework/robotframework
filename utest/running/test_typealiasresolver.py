import sys
import unittest

if sys.version_info >= (3, 12):
    from _test_typealiasresolver import *  # noqa F403


if __name__ == "__main__":
    unittest.main()
