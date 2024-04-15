"""
Options for the Apex Console Driver.
"""

from dataclasses import dataclass
import logging


@dataclass
class Options:
    """
    Options for the Apex driver.

    Args:
        apex_email (str): Email address for the Apex account
        apex_password (str): Password for the Apex account
        use_chrome_profile (bool): Use your chrome save data to elliminate
            the need to login every time (disable if you are going to run
            multiple instances of the driver)
        use_headless (bool): Run the driver in headless mode (disable if
            you want to see the browser(s))
    """

    apex_email: str
    apex_password: str
    cookies: dict = None
    use_headless: bool = False  # for playwriteAuth only
    log_level: (
        logging.DEBUG
        | logging.INFO
        | logging.WARNING
        | logging.ERROR
        | logging.CRITICAL
    ) = logging.INFO
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
        " (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    )
