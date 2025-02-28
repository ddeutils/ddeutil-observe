from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DB_INDEXES_NAMING_CONVENTION: dict[str, str] = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


# NOTE:
#       Attributes that are lazy-loading relationships, deferred columns or
#   expressions, or are being accessed in expiration scenarios can take
#   advantage of the AsyncAttrs mixin.
#   Read more: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html -
#       #preventing-implicit-io-when-using-asyncsession
#
class Base(AsyncAttrs, DeclarativeBase):
    """Subclass of DeclarativeBase that use to implement this application
    custom metadata.
    """

    __abstract__ = True

    metadata = MetaData(
        naming_convention=DB_INDEXES_NAMING_CONVENTION,
        # NOTE: In SQLite schema, the value should be `main` only because it
        #   does not implement with schema system.
        schema="main",
    )

    def __repr__(self) -> str:
        columns = ", ".join(
            [
                f"{k}={repr(v)}"
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )
        return f"<{self.__class__.__name__}({columns})>"


Col = mapped_column
Dtype = Mapped
