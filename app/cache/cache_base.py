import logging


class CacheBase:
    """Mechanisms inherent in all service Cache operations."""

    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
