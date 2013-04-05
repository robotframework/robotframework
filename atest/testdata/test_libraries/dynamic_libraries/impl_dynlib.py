def impl_say_hello(first_name="John"):
    print "Hello %s." % first_name

def impl_say_goodbye(first_name="John", last_name="Smith"):
    print "Good bye %s %s." % (first_name, last_name)

def impl_say_something_to(message, to_whom='You', from_who='Me'):
    print "%s! %s. -BR, %s" % (to_whom, message, from_who)

def impl_a_keyword(a, b=1):
    print a, b