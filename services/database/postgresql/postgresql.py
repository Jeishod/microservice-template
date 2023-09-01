import socket
from contextlib import suppress
from urllib.parse import quote

from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy import (
    MetaData,
    Table,
)
from sqlalchemy.exc import (
    DatabaseError,
    IntegrityError,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    engine,
    session,
)
from sqlalchemy.orm import declarative_base

from models.pydantic import (
    DatabaseException,
    ObjectAlreadyExists,
)
from services.database import Database
from services.database.postgresql.settings import PostgreSQLParams
from services.services_base import ServiceBase


class SessionHandler:
    """
    Intermediate class for managing temporarily-created session and handling exceptions.
    Main purpose: avoiding code duplication
    !!! Warning: hardcoded always try to commit when errors not handled

    :param session(AsyncSession): managed session must be passed from outside

    """

    def __init__(self, session: session.AsyncSession):  # pylint:disable=redefined-outer-name
        self.session = session

    async def __aenter__(self) -> session.AsyncSession:
        await self.session.begin()
        return self.session

    async def __aexit__(self, exception_type: type, exception: Exception, _traceback) -> None:
        """Handling errors that occur when working with the database"""
        try:
            if exception_type:
                raise exception_type(exception) from exception
            await self.session.commit()
        except IntegrityError as integrity_error:
            await self.session.rollback()
            if hasattr(integrity_error.orig, "sqlstate"):
                if integrity_error.orig.sqlstate == UNIQUE_VIOLATION:  # type: ignore[union-attr]
                    raise ObjectAlreadyExists(message_prefix="Object already exists") from integrity_error
        except (DatabaseError, OSError) as database_error:
            await self.session.rollback()
            raise DatabaseException(message="Failed to perform database operation") from database_error
        except Exception as e:  # pylint:disable=broad-exception-caught
            await self.session.rollback()
            if isinstance(e, exception_type):
                raise e
        finally:
            with suppress(Exception):
                await self.session.close()


class PostgreSQL(ServiceBase, Database):  # pylint: disable=too-many-instance-attributes
    """
    Implementing a PostgreSQL database
    - loading table metadata from the database (_prepare_metadata)
    - preparation of objects for group insertion (_prepare_objects)
    - perform bulk insert (bulk_create)
    - when receiving metadata, they are stored in the dictionary, for caching (_fetched_tables)
    """

    _params: PostgreSQLParams
    _engine: engine.AsyncEngine
    _metadata: MetaData
    _session_maker: async_sessionmaker[session.AsyncSession]
    _fetched_tables: dict[str, Table]
    _session: session.AsyncSession
    _autocommit: bool

    def __init__(self, params: PostgreSQLParams) -> None:
        """
        Initialize settings
        :param connection_params(PostgreSQLParams): Database connection parameters and settings for working with it
        """
        super().__init__()
        self._params = params
        self._fetched_tables = {}
        self._metadata = MetaData()
        self._base = declarative_base(metadata=self._metadata)
        self._autocommit = True

    @staticmethod
    def _make_url(params: PostgreSQLParams) -> str:
        """An example of a private method for generating a connection string"""
        username: str = quote(params.USERNAME)
        password: str = quote(params.PASSWORD)
        port: int = params.PORT
        host: str = params.HOST + (f":{port}" if port else "")
        database: str = params.DATABASE
        return f"postgresql+asyncpg://{username}:{password}@{host}/{database}"

    async def connect(self) -> None:
        """Database connecting"""
        try:
            self._engine = create_async_engine(
                url=self._make_url(params=self._params),
                pool_size=self._params.POOL_SIZE,
                echo_pool=self._params.ECHO_POOL,
                pool_pre_ping=True,
                connect_args={
                    "server_settings": {
                        "statement_timeout": "5000",
                    },
                },
            )
            self._session_maker = async_sessionmaker(bind=self._engine, expire_on_commit=False)
        except socket.gaierror:
            clean_params: PostgreSQLParams = self._params.copy(exclude={"PASSWORD"})
            self.logger.exception(f"Invalid postgresql connection params: {clean_params}")
            raise

    def session(self) -> SessionHandler:
        """Create an intermediate session"""
        return SessionHandler(session=self._session_maker())
