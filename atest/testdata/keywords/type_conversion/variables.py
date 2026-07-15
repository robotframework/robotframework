class NoClass:

    def __getattribute__(self, name):
        if name == "__class__":
            raise AttributeError(name)
        return super().__getattribute__(name)


def get_variables():
    return {"NO_CLASS": NoClass()}
