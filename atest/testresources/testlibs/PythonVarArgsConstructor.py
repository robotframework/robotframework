class PythonVarArgsConstructor:
    
    def __init__(self, mandatory, *varargs):
        self.mandatory = mandatory
        self.varargs = varargs

    def get_args(self):
        return self.mandatory, ' '.join(self.varargs)

