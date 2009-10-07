def simple_keyword():
    """Log a message"""
    print 'You have used the simplest keyword.'

def greet(name):
    """Logs a friendly greeting to person given as argument"""
    print 'Hello %s!' % name

def multiply_by_two(number):
    """Returns the given number multiplied by two
    
    The result is always a floating point number.
    This keyword fails if the given `number` cannot be converted to number.
    """
    return float(number) * 2

def numbers_should_be_equal(first, second):
    print '*DEBUG* Got arguments %s and %s' % (first, second)
    if float(first) != float(second):
        raise AssertionError('Given numbers are unequal!')
