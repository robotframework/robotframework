import unittest
from pathlib import Path


class TestZipSafe(unittest.TestCase):

    def test_no_unsafe__file__usages(self):
        root = Path(__file__).absolute().parent.parent.parent / 'src/robot'

        def unsafe__file__usage(line, path):
            if ('__file__' not in line or '# zipsafe' in line
                    or path.parent == root / 'htmldata/testdata'):
                return False
            return '__file__' in line.replace("'__file__'", '').replace('"__file__"', '')

        for path in root.rglob('*.py'):
            with path.open(encoding='UTF-8') as file:
                for lineno, line in enumerate(file, start=1):
                    if unsafe__file__usage(line, path):
                        raise AssertionError(f'Unsafe __file__ usage in {path} '
                                             f'on line {lineno}.')


if __name__ == '__main__':
    unittest.main()
