# TODO: Are these tests run somehow?????????????????


import robot.result.jsparser as jsparser

def test_timestamp():
    context = jsparser.Context()
    time = context.timestamp('20110603 12:00:00.000')
    assert time == 0
    time = context.timestamp('N/A')
    assert time == -1
    time = context.timestamp('20110603 12:00:01.000')
    assert time == 1000

def test_stats_when_failing_suite_teardown():
    context = jsparser.Context()
    context.collect_stats()
    context.add_test(1,1)
    child_stats = context.dump_stats()
    assert child_stats == [1, 1, 1, 1]
    context.teardown_failed()
    parent_stats = context.dump_stats()
    assert child_stats == [1, 0, 1, 0]
    assert parent_stats == [1, 0, 1, 0]

def test_link_creation():
    key = [4,'W',6]
    context = jsparser.Context()
    context.start_suite("Foo")
    context.start_suite("Bar")
    context.start_test("Zoo")
    context.start_keyword()
    context.create_link_to_current_location(key)
    context.end_keyword()
    context.end_test()
    context.end_suite()
    context.end_suite()
    link = context.link_to(key)
    assert link == "keyword_Foo.Bar.Zoo.0"

def test_2_links():
    key1 = [1,'W',2]
    key2 = [2,'W',5]
    context = jsparser.Context()
    context.start_suite("Bar")
    _kw(context, lambda ctx: ctx.create_link_to_current_location(key1))
    context.start_test("Test")
    context.start_keyword()
    _kw(context)
    _kw(context, lambda ctx: ctx.create_link_to_current_location(key2))
    context.end_keyword()
    context.end_test()
    context.end_suite()
    link2 = context.link_to(key2)
    link1 = context.link_to(key1)
    assert link1 == "keyword_Bar.0"
    assert link2 == "keyword_Bar.Test.0.1"

def _kw(context, inner_func=None):
    context.start_keyword()
    if inner_func: inner_func(context)
    context.end_keyword()

def _and(*funcs):
    def and_func(context):
        for func in funcs:
            func(context)
    return and_func

def test_link_to_subkeyword():
    key = [1, 'W', 542]
    context = jsparser.Context()
    context.start_suite("Boo") #suite_Boo
    context.start_test("Goo") #test_Boo.Goo
    _kw(context) #keyword_Boo.Goo.0
    _kw(context, _and(_kw, _kw, _kw)) #keyword_Boo.Goo.1.[0,1,2]
    context.start_keyword() #keyword_Boo.Goo.2
    _kw(context) #keyword_Boo.Goo.2.0
    context.start_keyword() #keyword_Boo.Goo.2.1
    context.create_link_to_current_location(key)
    _kw(context)  #keyword_Boo.Goo.2.1
    _kw(context)  #keyword Boo.Goo.2.2
    context.end_keyword()
    context.end_test()
    context.end_suite()
    link = context.link_to(key)
    assert link == "keyword_Boo.Goo.2.1"

def test_link_to_suite_teardown():
    pkey = [5, 'W', 321]
    skey = [4, 'W', 3214]
    context = jsparser.Context()
    context.start_suite("Suit")
    _kw(context) #Suite setup
    context.start_suite("Subsuite")
    context.start_test("Test1")
    _kw(context)
    context.end_test()
    _kw(context, lambda ctx: ctx.create_link_to_current_location(skey))
    context.end_suite()
    _kw(context, lambda ctx: ctx.create_link_to_current_location(pkey))
    context.end_suite()
    link1 = context.link_to(skey)
    link2 = context.link_to(pkey)
    assert link1 == "keyword_Suit.Subsuite.0"
    assert link2 == "keyword_Suit.1"
