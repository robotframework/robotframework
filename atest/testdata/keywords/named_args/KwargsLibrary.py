class KwargsLibrary:

    def one_named(self, named=None):
        return named

    def two_named(self, fst=None, snd=None):
        return f"{fst}, {snd}"

    def four_named(self, a=None, b=None, c=None, d=None):
        return f"{a}, {b}, {c}, {d}"

    def mandatory_and_named(self, a, b, c=None):
        return f"{a}, {b}, {c}"

    def mandatory_named_and_varargs(self, mandatory, d1=None, d2=None, *varargs):
        return f"{mandatory}, {d1}, {d2}, [{', '.join(varargs)}]"
