import os


def reports_should_be_equal(file1, file2):
    with open(file1.replace('/', os.sep)) as f1:
        content1 = f1.readlines()
        with open(file2.replace('/', os.sep)) as f2:
            content2 = f2.readlines()
            for l1, l2 in zip(content1, content2):
                if not _lines_are_equal(l1, l2):
                    raise AssertionError('%r\n is not same as\n%r' % (l1, l2))
            if len(content1) != len(content2):
                raise AssertionError("file %r len %d is different "
                                     "than file %r len %d" %
                                     (file1, len(content1),
                                      file2, len(content2)))


def _lines_are_equal(line1, line2):
    for changing in ('generatedTimestamp', 'generatedMillis'):
        if changing in line1 and changing in line2:
            return True
    return line1 == line2
