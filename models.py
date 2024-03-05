from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[str] = mapped_column(Integer())
    channel_name: Mapped[str] = mapped_column(String(256))
    message: Mapped[str] = mapped_column(String(6000))

    def __repr__(self) -> str:
        return f"ID(id={self.id!r}, channel={self.channel_name!r}, message=\n{self.message!r})"
