"""
This module contains the cryptographic functions used to generate the signature
"""

import math
import time


def time_signature():
    """
    Generate a signature for the request.
    """
    key = list(
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    )

    e = int(time.time() * 1000)
    t = ""
    while e > 0:
        t = key[e % 64] + t
        e = math.floor(e / 64)

    return t
