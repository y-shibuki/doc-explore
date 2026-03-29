from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    mtime: Mapped[float] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    ext: Mapped[str] = mapped_column(nullable=False)
    indexed_at: Mapped[str] = mapped_column(nullable=False)

    tags: Mapped[list["Tag"]] = relationship(
        secondary="file_tags", back_populates="files", lazy="selectin"
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    files: Mapped[list[File]] = relationship(
        secondary="file_tags", back_populates="tags", lazy="selectin"
    )


class FileTag(Base):
    __tablename__ = "file_tags"
    __table_args__ = (UniqueConstraint("file_id", "tag_id"),)

    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class ScanLog(Base):
    __tablename__ = "scan_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[str] = mapped_column(nullable=False)
    finished_at: Mapped[str | None] = mapped_column(nullable=True)
    files_added: Mapped[int] = mapped_column(default=0)
    files_updated: Mapped[int] = mapped_column(default=0)
    files_deleted: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(nullable=False)
