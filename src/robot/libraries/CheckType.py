
from robot.utils import type_name

class CheckType:
    def should_be_dictionary(self, item, msg=None):
        """Fails if the given `item` is not a dictionary.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not a dictionary.

        Returns:
            bool: True if the `item` is a dictionary.
        
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, dict):
            return True
        else:
            raise AssertionError(msg or f"item is not a dictionary, got {type_name(item)}: {item}")
    
    def should_be_object(self, item, msg=None):
        """Fails if the given `item` is not an object.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not an object.

        Returns:
            bool: True if the `item` is an object.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, object):
            return True
        else:
            raise AssertionError(msg or f"item is not a object, got {type_name(item)}: {item}")
    
    def should_be_integer(self, item, msg=None):
        """Fails if the given `item` is not an integer.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not an integer.

        Returns:
            bool: True if the `item` is an integer.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, int) and not isinstance(item, bool):
            return True
        else:
            raise AssertionError(msg or f"item is not a integer, got {type_name(item)}: {item}")
    
    def should_be_list(self, item, msg=None):
        """Fails if the given `item` is not a list.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not a list.

        Returns:
            bool: True if the `item` is a list.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, list):
            return True
        else:
            raise AssertionError(msg or f"item is not a list, got {type_name(item)}: {item}")
    
    def should_be_boolean(self, item, msg=None):
        """Fails if the given `item` is not a boolean.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not a boolean.

        Returns:
            bool: True if the `item` is a boolean.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, bool):
            return True
        else:
            raise AssertionError(msg or f"item is not a boolean, got {type_name(item)}: {item}")
        
    def should_be_float(self, item, msg=None):
        """Fails if the given `item` is not a float.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not a float.

        Returns:
            bool: True if the `item` is a float.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, float):
            return True
        else:
            raise AssertionError(msg or f"item is not a float, got {type_name(item)}: {item}")

    def should_be_none_type(self, item, msg=None):
        """Fails if the given `item` is not of NoneType.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not of NoneType.

        Returns:
            bool: True if the `item` is of NoneType.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if item is None:
            return True
        else:
            raise AssertionError(msg or f"item is not of NoneType, got {type_name(item)}: {item}")

    def should_be_tuple(self, item, msg=None):
        """Fails if the given `item` is not a tuple.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not a tuple.

        Returns:
            bool: True if the `item` is a tuple.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, tuple):
            return True
        else:
            raise AssertionError(msg or f"item is not a tuple, got {type_name(item)}: {item}")

    def should_be_set(self, item, msg=None):
        """Fails if the given `item` is not a set.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is not a set.

        Returns:
            bool: True if the `item` is a set.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if isinstance(item, set):
            return True
        else:
            raise AssertionError(msg or f"item is not a set, got {type_name(item)}: {item}")

    

    def should_not_be_dictionary(self, item, msg=None):
        """Fails if the given `item` is a dictionary.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is a dictionary.

        Returns:
            bool: True if the `item` is not a dictionary.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, dict):
            return True
        else:
            raise AssertionError(msg or f"item is a dictionary, got {type_name(item)}: {item}")
    
    def should_not_be_object(self, item, msg=None):
        """Fails if the given `item` is an object.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is an object.

        Returns:
            bool: True if the `item` is not an object.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, object):
            return True
        else:
            raise AssertionError(msg or f"item is a object, got {type_name(item)}: {item}")
    
    def should_not_be_integer(self, item, msg=None):
        """Fails if the given `item` is an integer.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is an integer.

        Returns:
            bool: True if the `item` is not an integer.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, int):
            return True
        else:
            raise AssertionError(msg or f"item is a integer, got {type_name(item)}: {item}")
    
    def should_not_be_list(self, item, msg=None):
        """Fails if the given `item` is a list.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is a list.

        Returns:
            bool: True if the `item` is not a list.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, list):
            return True
        else:
            raise AssertionError(msg or f"item is a list, got {type_name(item)}: {item}")

    def should_not_be_boolean(self, item, msg=None):
        """Fails if the given `item` is a boolean.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is a boolean.

        Returns:
            bool: True if the `item` is not a boolean.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, bool):
            return True
        else:
            raise AssertionError(msg or f"item is a boolean, got {type_name(item)}: {item}")
    
    def should_not_be_float(self, item, msg=None):
        """Fails if the given `item` is a float.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is a float.

        Returns:
            bool: True if the `item` is not a float.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, float):
            return True
        else:
            raise AssertionError(msg or f"item is a float, got {type_name(item)}: {item}")

    def should_not_be_none_type(self, item, msg=None):
        """Fails if the given `item` is of NoneType.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is of NoneType.

        Returns:
            bool: True if the `item` is not of NoneType.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if item is not None:
            return True
        else:
            raise AssertionError(msg or f"item is of NoneType, got {type_name(item)}: {item}")

    def should_not_be_tuple(self, item, msg=None):
        """Fails if the given `item` is a tuple.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is a tuple.

        Returns:
            bool: True if the `item` is not a tuple.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, tuple):
            return True
        else:
            raise AssertionError(msg or f"item is a tuple, got {type_name(item)}: {item}")

    def should_not_be_set(self, item, msg=None):
        """Fails if the given `item` is a set.

        Args:
            item: The item to be checked.

        Raises:
            AssertionError: If the `item` is a set.

        Returns:
            bool: True if the `item` is not a set.
            
        The default error message can be overridden with the optional ``msg`` argument.
        """
        if not isinstance(item, set):
            return True
        else:
            raise AssertionError(msg or f"item is a set, got {type_name(item)}: {item}")