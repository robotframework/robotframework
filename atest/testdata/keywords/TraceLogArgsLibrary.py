class TraceLogArgsLibrary:

    def only_mandatory(self, mand1, mand2):
        pass

    def mandatory_and_default(self, mand, default="default value"):
        pass

    def multiple_default_values(self, a=1, a2=2, a3=3, a4=4):
        pass

    def mandatory_and_varargs(self, mand, *varargs):
        pass

    def kwargs(self, **kwargs):
        pass

    def all_args(self, positional, *varargs, **kwargs):
        pass

    def return_object_with_non_ascii_repr(self):
        class NonAsciiRepr:
            def __repr__(self):
                return 'Hyv\xe4'
        return NonAsciiRepr()

    def return_object_with_invalid_repr(self):
        class InvalidRepr:
            def __repr__(self):
                raise ValueError
        return InvalidRepr()

    def embedded_arguments(self, *args):
        assert args == ('bar', 'Embedded Arguments')

    embedded_arguments.robot_name = 'Embedded Arguments "${a}" and "${b}"'
