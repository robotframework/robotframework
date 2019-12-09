import unittest

from robot.utils.table_of_content import add_toc, _get_headings, _create_toc

EXAMPLE_DOC_TOC = """Simple library

%TABLE_OF_CONTENTS%

= 1 Heading =

Some text here for chapter 1.

= 2 Heading =

Second chapter text there.

Second paragraph.
"""

EXAMPLE_DOC_NO_HEADING = """Simple library

%TABLE_OF_CONTENTS%

Some text here for library.

= This is not heading

No heading here =

This = is not = heading

Other text
"""


class TestTableOfContentLibdoc(unittest.TestCase):

    def test_no_toc(self):
        test_doc = 'Library doc'
        doc = add_toc(test_doc)
        self.assertEqual(doc, test_doc, 'Doc should not have been created.')

        test_doc = 'Foo %TABLE_OF_CONTENT% Bar'
        doc = add_toc(test_doc)
        self.assertEqual(doc, test_doc, 'Doc should not have been created.')

        test_doc = 'Foo %TABLE_OF_CONTENT%'
        doc = add_toc(test_doc)
        self.assertEqual(doc, test_doc, 'Doc should not have been created.')

        test_doc = '%TABLE_OF_CONTENT% Bar'
        doc = add_toc(test_doc)
        self.assertEqual(doc, test_doc, 'Doc should not have been created.')

    def test_add_toc(self):
        doc = add_toc(EXAMPLE_DOC_TOC)
        doc = doc.splitlines()
        self.assertEqual('== Table of contents ==', doc[2], 'TOC should have been generated.')
        self.assertEqual('', doc[3], 'TOC should have been generated.')
        self.assertEqual('- `1 Heading`', doc[4], 'TOC should have been generated.')
        self.assertEqual('- `2 Heading`', doc[5], 'TOC should have been generated.')
        self.assertEqual('- `Importing`', doc[6], 'TOC should have been generated.')
        self.assertEqual('- `Shortcuts`', doc[7], 'TOC should have been generated.')
        self.assertEqual('- `Keywords`', doc[8], 'TOC should have been generated.')
        self.assertEqual('', doc[9], 'TOC should have been generated.')
        self.assertEqual('= 1 Heading =', doc[10], 'TOC should have been generated.')

    def test_get_headings(self):
        headings = _get_headings(EXAMPLE_DOC_TOC)
        self.assertEqual(headings, ['- `1 Heading`', '- `2 Heading`'], 'Could not find headings.')

        headings = _get_headings(EXAMPLE_DOC_NO_HEADING)
        self.assertEqual(headings, [], 'No headings in doc.')

        headings = _get_headings('== This is not heading =')
        self.assertEqual(headings, [], 'No headings in doc.')

        headings = _get_headings(' = This is not heading =')
        self.assertEqual(headings, [], 'No headings in doc.')

        headings = _get_headings('= This is not heading = ')
        self.assertEqual(headings, [], 'No headings in doc.')

    def test_create_toc(self):
        headings = ['- `1 Heading`', '- `2 Heading`']
        toc = _create_toc(headings)
        expected_toc = ['== Table of contents ==', '']
        expected_toc.extend(headings)
        expected_toc.extend(['- `Importing`', '- `Shortcuts`', '- `Keywords`'])
        self.assertEqual(toc, expected_toc)

        toc = _create_toc([])
        expected_toc = ['== Table of contents ==', '']
        expected_toc.extend(['- `Importing`', '- `Shortcuts`', '- `Keywords`'])
        self.assertEqual(toc, expected_toc)
