"""
This module includes general functions needed for the qc procedures.

Functions:
    - :py:meth:`~qc_general.general_functions.start_qc`
    - :py:meth:`~qc_general.general_functions.start_qc_message`
    - :py:meth:`~qc_general.general_functions.check_property`
"""
from functools import wraps
from typing import Any, Optional, Tuple, List, Union


def start_qc_message(test_name: str):
    """Prints a customized message."""
    if isinstance(test_name, str):
        print(f"\n{120 * '-'}\n###### Check {test_name} ######")


def start_qc(func):
    """Prints the name of the QC check."""

    @wraps(func)
    def inner(*arg, **kwargs):
        func_name = func.__name__
        split_parts = func_name.replace("_", " ")
        print(f"\n{120 * '-'}\n###### {split_parts.upper()} ######")
        return func(*arg, **kwargs)

    return inner


def check_property(prop: Any,
                   specified_property: Any,
                   test_result: Optional[bool] = None,
                   additional_message: Optional[Union[str, List[str]]] = '',
                   log_op: Optional[str] = '') -> Tuple[bool, str]:
    """
    Check if raster/vector attribute is the same as specified attribute.

    :param prop: e.g. GTiff (raster driver)
    :type prop: str, int or list
    :param specified_property: e.g. GTiff
    :type specified_property: str, int or list
    :param test_result: set True/False if other test was run, and only message is needed
    :type test_result: bool or None, optional
    :param additional_message: additional info
    :type additional_message: str, optional
    :param log_op: logical operator to compare property with specified property, defaults to ==
    :type log_op: str, optional
    :return: Test result and a message for the QC report. (True/False, Message)
    :rtype: tuple (bool, str)
    """

    result = test_result
    if test_result is None:
        if not log_op:
            result = prop == specified_property
        elif log_op == "<":
            result = prop < specified_property
        elif log_op == ">":
            result = prop > specified_property
        elif log_op == "<=":
            result = prop <= specified_property
        elif log_op == ">=":
            result = prop >= specified_property

    if log_op:
        log_op += " "

    message = f"{'Passed' if result else 'Failed'}.\n" \
              f"Specifications: '{log_op}{specified_property}'\n" \
              f"Tested file: '{prop}'"

    if additional_message:
        message += f"\nInfo: {''.join(additional_message)}"

    print(f"\n###### TEST RESULT ######\n{message}\n\n")

    return result, message
