from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

@keyword(name="User ${user} Selects ${item} From Webshop")
def user_selects_from_webshop(user, item):
    print "This is always executed"
    return user, item

@keyword(name="${prefix:Given|When|Then} this \"${item}\" ${no good name for this arg ...}")
def this(ignored_prefix, item, somearg):
    print "%s-%s" % (item, somearg)

@keyword(name="My embedded ${var}")
def my_embedded(var):
    BuiltIn().should_be_equal(var, "warrior")

@keyword(name="${x:x} gets ${y:\w} from the ${z:.}")
def gets_from_the(x, y, z):
    BuiltIn().should_be_equal("%s-%s-%s" % (x, y, z), "x-y-z")

@keyword(name="${a}-lib-${b}")
def mult_match1(a, b):
    print "%s-lib-%s" % (a, b)

@keyword(name="${a}+lib+${b}")
def mult_match2(a, b):
    print "%s+lib+%s" % (a, b)

@keyword(name="${a}*lib*${b}")
def mult_match3(a, b):
    print "%s*lib*%s" % (a, b)

@keyword(name="I execute \"${x:[^\"]*}\"")
def i_execute(x):
    BuiltIn().should_be_equal(x, "foo")

@keyword(name="I execute \"${x:bar}\" with \"${y:...}\"")
def i_execute_with(x, y):
    BuiltIn().should_be_equal(x, "bar")
    BuiltIn().should_be_equal(y, "zap")

@keyword(name="Result of ${a:\d+} ${operator:[+-]} ${b:\d+} is ${result}")
def result_of_is(a, operator, b, result):
    BuiltIn().should_be_true(eval("%s%s%s" % (a, operator, b)), result)

@keyword(name="I want ${integer:whatever} and ${string:everwhat} as variables")
def i_want_as_variables(integer, string):
    BuiltIn().should_be_equal(integer, 42)
    BuiltIn().should_be_equal(string, "42")

@keyword(name="Today is ${date:\d{4\}-\d{2\}-\d{2\}}")
def today_is(date):
    BuiltIn().should_be_equal(date, "2011-06-21")

@keyword(name="Today is ${day1:\w{6,9\}} and tomorrow is ${day2:\w{6,9\}}")
def today_is_and_tomorrow_is(day1, day2):
    BuiltIn().should_be_equal(day1, "Tuesday")
    BuiltIn().should_be_equal(day2, "Wednesday")

@keyword(name="Literal ${Curly:{} Brace")
def literal_brace(curly):
    BuiltIn().should_be_equal(curly, "{")

@keyword(name="Literal ${Curly:\}} Brace")
def literal_escaped_brace(curly):
    BuiltIn().should_be_equal(curly, "}")

@keyword(name="Custom Regexp With Escape Chars e.g. ${1E:\\\\\\\\}, ${2E:\\\\\\\\\\\\\\\\} and ${PATH:c:\\\\\\\\temp\\\\.*}")
def custom_regexp_with_escape_chars(e1, e2, path):
    BuiltIn().should_be_equal(e1, "\\")
    BuiltIn().should_be_equal(e2, "\\\\")
    BuiltIn().should_be_equal(path, "c:\\temp\\test.txt")

@keyword(name="Custom Regexp With ${pattern:\\\\\\\\\\}}")
def custom_regexp_with(pattern):
    BuiltIn().should_be_equal(pattern, "\\}")

@keyword(name="Grouping ${x:Cu(st|ts)(om)?} ${y:Regexp\(?erts\)?}")
def grouping(x, y):
    return "%s-%s" % (x, y)

@keyword(name="Wrong ${number} of embedded ${args}")
def too_few_args_here(arg):
    pass

@keyword(name="Optional ${nonembedded} Args Are ${okay}")
def optional_args_are_okay(nonembedded=1, okay=2, indeed=3):
    pass

@keyword(name="Star Args With ${embedded} Args Are ${okay}")
def star_args_are_okay(*args):
    return args
