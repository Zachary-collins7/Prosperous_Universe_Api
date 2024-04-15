"""
Decorators for the puapi package
"""

import time
from functools import wraps
from typing import Callable, Iterable


def retry_on_exception(
    *,  # enforce keyword-only arguments
    retries: int = 3,
    retry_delay: int = 0,
    catch: Iterable = (Exception,),
    on_error_callback: Callable[[Exception], None] | None = None,
):
    """
    decorator to retry a function on exception

    Example:
    ```
    @retry_on_exception(retries=3, backoff=1, catch=(Exception,))
    def my_function():
        pass
    ```
    :param retries: number of retries
    :param backoff: time to wait between retries
    :param catch: exceptions to catch
    :param on_error_callback: callback to call on error
    :return: wrapper function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except catch as e:
                    last_error = e
                    if on_error_callback:
                        on_error_callback(e)
                time.sleep(retry_delay)
            raise last_error

        return wrapper

    return decorator
