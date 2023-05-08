from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db_common import Base


class DbPublisher(Base):
    __tablename__ = "publisher"

    publisher_id: Mapped[int] = mapped_column(primary_key=True)
    publisher_name: Mapped[str] = mapped_column(String(50), nullable=False)
    publisher_code: Mapped[str] = mapped_column(String(10), nullable=False)
