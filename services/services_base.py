import logging


class ServiceBase:
    """Mechanisms inherent in all service services"""

    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
