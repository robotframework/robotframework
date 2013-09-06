class DictWithoutHasKey(dict):

    def has_key(self, key):
        raise NotImplementedError('Emulating collections.Mapping which '
                                  'does not have `has_key`.')


def get_dict_without_has_key(**items):
    return DictWithoutHasKey(**items)
