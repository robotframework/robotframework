from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


ROBOT_AUTO_KEYWORDS = False
should_be_equal = BuiltIn().should_be_equal
log = logger.write


@keyword(name="User ${user} Selects ${item} From Webshop")
def user_selects_from_webshop(user, item):
    log("This is always executed")
    return user, item


@keyword(name='${prefix:Given|When|Then} this "${item}" ${no good name for this arg ...}')
def this(ignored_prefix, item, somearg):
    log("%s-%s" % (item, somearg))


@keyword(name="My embedded ${var}")
def my_embedded(var):
    should_be_equal(var, "warrior")


@keyword(name=r"${x:x} gets ${y:\w} from the ${z:.}")
def gets_from_the(x, y, z):
    should_be_equal("%s-%s-%s" % (x, y, z), "x-y-z")


@keyword(name="${a}-lib-${b}")
def mult_match1(a, b):
    log("%s-lib-%s" % (a, b))


@keyword(name="${a}+lib+${b}")
def mult_match2(a, b):
    log("%s+lib+%s" % (a, b))


@keyword(name="${a}*lib*${b}")
def mult_match3(a, b):
    log("%s*lib*%s" % (a, b))


@keyword(name='I execute "${x:[^"]*}"')
def i_execute(x):
    should_be_equal(x, "foo")


@keyword(name='I execute "${x:bar}" with "${y:...}"')
def i_execute_with(x, y):
    should_be_equal(x, "bar")
    should_be_equal(y, "zap")


@keyword(name=r"Result of ${a:\d+} ${operator:[+-]} ${b:\d+} is ${result}")
def result_of_is(a, operator, b, result):
    should_be_equal(eval("%s%s%s" % (a, operator, b)), float(result))


@keyword(name="I want ${integer:whatever} and ${string:everwhat} as variables")
def i_want_as_variables(integer, string):
    should_be_equal(integer, 42)
    should_be_equal(string, "42")


@keyword(name=r"Today is ${date:\d{4}-\d{2}-\d{2}}")
def today_is(date):
    should_be_equal(date, "2011-06-21")


@keyword(name=r"Today is ${day1:\w{6,9}} and tomorrow is ${day2:\w{6,9}}")
def today_is_and_tomorrow_is(day1, day2):
    should_be_equal(day1, "Tuesday")
    should_be_equal(day2, "Wednesday")


@keyword(name=r"Literal ${Curly:\{} Brace")
def literal_opening_curly_brace(curly):
    should_be_equal(curly, "{")


@keyword(name=r"Literal ${Curly:\}} Brace")
def literal_closing_curly_brace(curly):
    should_be_equal(curly, "}")


@keyword(name="Literal ${Curly:{}} Braces")
def literal_curly_braces(curly):
    should_be_equal(curly, "{}")


@keyword(name=r"Custom Regexp With Escape Chars e.g. ${1E:\\}, "
              r"${2E:\\\\} and ${PATH:c:\\temp\\.*}")
def custom_regexp_with_escape_chars(e1, e2, path):
    should_be_equal(e1, "\\")
    should_be_equal(e2, "\\\\")
    should_be_equal(path, "c:\\temp\\test.txt")


@keyword(name=r"Custom Regexp With ${escapes:\\\}}")
def custom_regexp_with_escapes_1(escapes):
    should_be_equal(escapes, r'\}')


@keyword(name=r"Custom Regexp With ${escapes:\\\{}")
def custom_regexp_with_escapes_2(escapes):
    should_be_equal(escapes, r'\{')


@keyword(name=r"Custom Regexp With ${escapes:\\{}}")
def custom_regexp_with_escapes_3(escapes):
    should_be_equal(escapes, r'\{}')


@keyword(name=r"Grouping ${x:Cu(st|ts)(om)?} ${y:Regexp\(?erts\)?}")
def grouping(x, y):
    return f'{x}-{y}'


@keyword(name="Wrong ${number} of embedded ${args}")
def too_few_args_here(arg):
    pass


@keyword(name="Optional non-${embedded} Args Are ${okay}")
def optional_args_are_okay(embedded=1, okay=2, extra=3):
    return embedded, okay, extra


@keyword(name="Varargs With ${embedded} Args Are ${okay}")
def varargs_are_okay(*args):
    return args


@keyword('It is ${vehicle:a (car|ship)}')
def same_name_1(vehicle):
    log(vehicle)


@keyword('It is ${animal:a (dog|cat)}')
def same_name_2(animal):
    log(animal)


@keyword('It is ${animal:a (cat|cow)}')
def same_name_3(animal):
    log(animal)


@keyword('It is totally ${same}')
def totally_same_1(arg):
    raise Exception('Not executed')


@keyword('It is totally ${same}')
def totally_same_2(arg):
    raise Exception('Not executed')


@keyword('Number of ${animals} should be')
def number_of_animals_should_be(animals, count, activity='walking'):
    log(f'{count} {animals} are {activity}')


@keyword('Conversion with embedded ${number} and normal')
def conversion_with_embedded_and_normal(num1: int, /, num2: int):
    assert num1 == num2 == 42
