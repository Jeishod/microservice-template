import logging


class ManagersBase:
    """Mechanisms inherent in all service managers"""

    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
