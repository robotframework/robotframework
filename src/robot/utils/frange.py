#  Copyright 2008-2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


def frange(*args):
    """Like ``range()`` but accepts float arguments."""
    if all(isinstance(arg, (int, long)) for arg in args):
        return range(*args)
    start, stop, step = _get_start_stop_step(args)
    digits = max(_digits(start), _digits(stop), _digits(step))
    factor = pow(10, digits)
    return [x/float(factor) for x in range(int(round(start*factor)),
                                           int(round(stop*factor)),
                                           int(round(step*factor)))]


def _get_start_stop_step(args):
    if len(args) == 1:
        return 0, args[0], 1
    if len(args) == 2:
        return args[0], args[1], 1
    if len(args) == 3:
        return args
    raise TypeError('frange expected 1-3 arguments, got %d' % len(args))


def _digits(number):
    if not isinstance(number, str):
        number = repr(number)
    if 'e' in number:
        return _digits_with_exponent(number)
    if '.' in number:
        return _digits_with_fractional(number)
    return 0


def _digits_with_exponent(number):
    mantissa, exponent = number.split('e')
    mantissa_digits = _digits(mantissa)
    exponent_digits = int(exponent) * -1
    return max(mantissa_digits + exponent_digits, 0)


def _digits_with_fractional(number):
    fractional = number.split('.')[1]
    if fractional == '0':
        return 0
    return len(fractional)
