class TraceLogArgsLibrary(object):

    def only_mandatory(self, mand1, mand2):
        pass

    def mandatory_and_default(self, mand, default="default value"):
        pass

    def multiple_default_values(self, a=1, a2=2, a3=3, a4=4):
        pass

    def mandatory_and_varargs(self, mand, *varargs):
        pass

    def return_object_with_invalid_repr(self):
        return InvalidRepr()

    def return_object_with_non_ascii_string_repr(self):
        return ByteRepr()


class InvalidRepr:

    def __repr__(self):
        return u'Hyv\xe4'

class ByteRepr:

    def __repr__(self):
        return 'Hyv\xe4'