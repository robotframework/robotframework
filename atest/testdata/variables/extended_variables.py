class ExampleObject:
    
    def __init__(self, name='<noname>'):
        self.name = name

    def greet(self, name=None):
        if not name:
            return '%s says hi!' % self.name
        if name == 'FAIL':
            raise ValueError
        return '%s says hi to %s!' % (self.name, name)
    
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return "'%s'" % self.name


OBJ = ExampleObject('dude')
