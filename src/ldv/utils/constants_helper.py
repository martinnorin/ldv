"""Constants helper module. """

from typing import Any, List


class ConstantsHelper:
    """ Class for helper functions for constants. """

    @staticmethod
    def get_constants_values(constant_class: Any) -> List[str]:
        """Get constants values in class.

        Args:
            constant_class: the constant class

        Returns:
            a list of the constant values of the class

        """
        return [value
                for key, value
                in constant_class.__dict__.items()
                if not key.startswith('__') and not callable(key)]

    @staticmethod
    def get_constants_names(constant_class: Any) -> List[str]:
        """Get constants names in class.

        Args:
            constant_class: the constant class

        Returns:
            a list of the constant names of the class

        """

        return [key
                for key, _
                in constant_class.__dict__.items()
                if not key.startswith('__') and not callable(key)]

    @staticmethod
    def get_constants_dict(constant_class: Any) -> dict:
        """Get constants names and values of class.

        Args:
            constant_class: the constant class

        Returns:
            a dict of the constant names and values of the class

        """

        return {key: value
                for key, value
                in constant_class.__dict__.items()
                if not key.startswith('__') and not callable(key)}
