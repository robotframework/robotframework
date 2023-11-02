from functools import cached_property


class NonDataDescriptor:

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(instance)


class DataDescriptor(NonDataDescriptor):

    def __set__(self, instance, value):
        pass


class FailingNonDataDescriptor(NonDataDescriptor):

    def __get__(self, instance, owner):
        return 1/0


class FailingDataDescriptor(DataDescriptor):

    def __get__(self, instance, owner):
        return 1/0


class AvoidProperties:
    normal_property_called = 0
    classmethod_property_called = 0
    cached_property_called = 0
    non_data_descriptor_called = 0
    classmethod_non_data_descriptor_called = 0
    data_descriptor_called = 0
    classmethod_data_descriptor_called = 0

    def keyword(self):
        pass

    @property
    def normal_property(self):
        type(self).normal_property_called += 1
        return self.normal_property_called

    @classmethod
    @property
    def classmethod_property(cls):
        cls.classmethod_property_called += 1
        return cls.classmethod_property_called

    @cached_property
    def cached_property(self):
        type(self).cached_property_called += 1
        return self.cached_property_called

    @NonDataDescriptor
    def non_data_descriptor(self):
        type(self).non_data_descriptor_called += 1
        return self.non_data_descriptor_called

    @classmethod
    @NonDataDescriptor
    def classmethod_non_data_descriptor(cls):
        cls.classmethod_non_data_descriptor_called += 1
        return cls.classmethod_non_data_descriptor_called

    @DataDescriptor
    def data_descriptor(self):
        type(self).data_descriptor_called += 1
        return self.data_descriptor_called

    @classmethod
    @DataDescriptor
    def classmethod_data_descriptor(cls):
        cls.classmethod_data_descriptor_called += 1
        return cls.classmethod_data_descriptor_called

    @FailingNonDataDescriptor
    def failing_non_data_descriptor(self):
        pass

    @classmethod
    @FailingNonDataDescriptor
    def failing_classmethod_non_data_descriptor(self):
        pass

    @FailingDataDescriptor
    def failing_data_descriptor(self):
        pass

    @classmethod
    @FailingDataDescriptor
    def failing_classmethod_data_descriptor(self):
        pass

