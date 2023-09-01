from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative


metadata = MetaData()


@as_declarative()
class SqlAlchemyBase:
    """SQLAlchemy Base"""

    class Meta:
        """Metadata"""

        metadata = metadata

    __tablename__: str
    metadata: MetaData
