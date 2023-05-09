from app.services.example_service.implementation.settings import ExampleServiceParams
from app.services.services_base import ServiceBase


class PostgreSQL(ServiceBase, Database):
    """
    Реализация работы с базой данных PostgreSQL
    - загрузка метаинформации таблиц из базы данных (_prepare_metadata)
    - подготовка объектов для групповой вставки (_prepare_objects)
    - выполнение групповой вставки (bulk_create)
    - при получении метаданных, они сохраняются в словаре, для кэширования (_fetched_tables)
    """

    _params: ExampleServiceParams

    def __init__(self, connection_params: ExampleServiceParams) -> None:
        super().__init__()
        self._params = connection_params
