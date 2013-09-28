#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from __future__ import with_statement

def difference_between_stuff(file1, file2):
    with open(file1) as f1:
        content1 = f1.readlines()
        with open(file2) as f2:
            content2 = f2.readlines()
            for l1,l2 in zip(content1, content2):
                if 'generatedTimestamp' in l1:
                    continue
                if 'generatedMillis' in l1:
                    continue
                if l1 != l2:
                    raise AssertionError('%r\n is not same as\n%r' % (l1, l2))
            if len(content1) != len(content2):
                raise AssertionError("file %r len %d is different "
                                     "than file %r len %d" %
                                     (file1, len(content1),
                                      file2, len(content2)))
