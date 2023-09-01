import logging


class DatabaseBase:
    """Mechanisms inherent in all service Database operations."""

    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
