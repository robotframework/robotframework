# Variable file used by variables.html


import sys


__all__ = ['obj', 'string2', 'list2', 'escapes2', 'list_with_escapes2',
           'LIST__list2', 'LIST__objects', 'LIST__empty_list2',
           'LIST__list_with_escapes2', 'string1','variable_file_var']


class ExampleObject:
    
    def __init__(self, name='<noname>'):
        self.name = name
    
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return "'%s'" % self.name
        

variable_file_var = 'Variable from a variable file'

obj = ExampleObject('dude')

string2 = 'Hi tellus'            # ${string2} | Hi tellus |
list2 = ['Hi','tellus']          # ${list2}  | Hi  | tellus
escapes2 = '1\\ 2\\\\ ${inv}'
list_with_escapes2 = escapes2.split()
LIST__list2 = ['Hi','tellus']    # @{list2}  | Hi  | tellus
LIST__empty_list2 = []
LIST__list_with_escapes2 = list_with_escapes2[:]
LIST__objects = ['string', obj, list2 ]

string1 = 'This is not added as variables.html already has it'
not_included = 'Not in __all__ thus not included'

