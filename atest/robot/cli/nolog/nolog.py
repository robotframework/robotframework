#!/usr/bin/env python
# -*- coding: utf-8 -*- 

def difference_between_stuff(eka, toka):
    with open(eka) as content1:
        with open(toka) as content2:
            for l1,l2 in zip(content1, content2):
                if 'generatedTimestamp' in l1:
                    continue
                if 'generatedMillis' in l1:
                    continue
                if l1 != l2:
                    raise AssertionError('%r\n is not same as\n%r' % (l1,l2) )
