from aiostorage_orm import AIORedisItem


class Projects(AIORedisItem):
    """Cached projects"""

    name: str
    description: str | None = None

    class Meta:  # pylint: disable=missing-class-docstring
        table = "project.{id}"
        ttl = 10
