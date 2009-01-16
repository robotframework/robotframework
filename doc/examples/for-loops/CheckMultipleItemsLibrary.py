class CheckMultipleItemsLibrary:

    def items_should_not_contain(self, value, *items):
        """Checks that none of the given 'items' contains the given 'value'."""

        items_containing_value = [ item for item in items if value in item ]
        if items_containing_value:
            message = "Items '%s' contains '%s'"
            message = message % (', '.join(items_containing_value), value)
            raise AssertionError(message)
