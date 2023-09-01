import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.router.router import router
from services import Services


class Application(FastAPI):
    """Setting up and preparing the launch of the service"""

    logger: logging.Logger
    services: Services

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.services = Services()

        super().__init__(
            title=self.services.config.APP_TITLE,
            description=self.services.config.APP_DESCRIPTION,
        )
        # Routers
        self.add_event_handler("startup", self.mount_routers)

        # Services. Comment service if not used in microservice.
        self.add_event_handler("startup", self.services.initialize_services)
        self.add_event_handler("startup", self.services.initialize_db)
        self.add_event_handler("startup", self.services.initialize_cache)
        self.add_event_handler("startup", self.services.initialize_broker)
        self.add_event_handler("startup", self.services.initialize_s3)

        # Shut down
        self.add_event_handler("shutdown", self.services.stop_broker)
        self.prepare_fastapi_instrumentator()

    def mount_routers(self) -> None:
        """Connecting routes"""
        self.include_router(router)

    def prepare_fastapi_instrumentator(self) -> None:
        """Instrument the app with default metrics and expose the metrics"""
        Instrumentator().instrument(self).expose(self)


app = Application()
