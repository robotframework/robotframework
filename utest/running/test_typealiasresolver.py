import sys
import unittest

if sys.version_info >= (3, 12):
    from _test_typealiasresolver import TestTypeAliasResolver as TestTypeAliasResolver

    if __name__ == "__main__":
        unittest.main()
