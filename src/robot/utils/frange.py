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
    result = []
    if len(args) == 1:
        start = 0
        stop = args[0]
        step = 1
    elif len(args) == 2:
        start = args[0]
        stop = args[1]
        step = 1
    elif len(args) == 3:
        start = args[0]
        stop = args[1]
        step = args[2]
    else:
        raise ValueError("invalid number of arguments")
    power_of_10 = max(_digits(start), _digits(stop), _digits(step))
    if power_of_10 == 0:
        result = range(int(start), int(stop), int(step))
    else:
        factor = pow(10, power_of_10)
        begin = int(start*factor)
        end = int(stop*factor)
        step2 = int(step*factor)
        result = [x/float(factor) for x in range(begin,end,step2)]
    return result

#algorithm inspired by http://stackoverflow.com/questions/6189956/easy-way-of-finding-decimal-places	
def _digits(number):
    digits = 0
    converted_number = repr(number)
    if 'e' in converted_number:
        exponent = int(converted_number.split('e')[1])
        if exponent < 0:
            exponent_digits = abs(exponent)
            mantissa_digits = _digits(converted_number.split('e')[0])
            digits = exponent_digits + mantissa_digits
        else:
            digits = 0
    else:
        list_of_strings = converted_number.split('.')
        if len(list_of_strings) == 1:
            digits = 0
        elif len(list_of_strings) == 2:
            if int(eval(str(number))) == float(number):
                digits = 0
            else:
                digits = len(list_of_strings[1].replace("'",""))
        else:
            raise ValueError("input is not a number")
    return digits
