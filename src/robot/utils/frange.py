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
    powerOf10 = max(_digits(start), _digits(stop), _digits(step))    
    if powerOf10 == 0:
        result = range(start, stop, step)
    else:
        factor = pow(10, powerOf10)
        begin = int(start*factor)
        end = int(stop*factor)
        step2 = int(step*factor)
        result = [x/float(factor) for x in range(begin,end,step2)]
    return result

#algorithm inspired by http://stackoverflow.com/questions/6189956/easy-way-of-finding-decimal-places	
def _digits(number):
    digits = 0
    convertedNumber = str(number)
    list_of_strings = convertedNumber.split('.')
    if len(list_of_strings) == 1:
        digits = 0
    elif len(list_of_strings) == 2:
        digits = len(list_of_strings[1])
    else:
        raise ValueError("input is not a number")
    return digits
