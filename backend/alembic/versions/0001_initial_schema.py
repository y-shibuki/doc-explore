"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-30

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("path", sa.String, nullable=False, unique=True),
        sa.Column("filename", sa.String, nullable=False),
        sa.Column("mtime", sa.Float, nullable=False),
        sa.Column("size", sa.Integer, nullable=False),
        sa.Column("ext", sa.String, nullable=False),
        sa.Column("indexed_at", sa.String, nullable=False),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
    )

    op.create_table(
        "file_tags",
        sa.Column(
            "file_id", sa.Integer, sa.ForeignKey("files.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.UniqueConstraint("file_id", "tag_id"),
    )

    op.create_table(
        "scan_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("started_at", sa.String, nullable=False),
        sa.Column("finished_at", sa.String, nullable=True),
        sa.Column("files_added", sa.Integer, nullable=False, server_default="0"),
        sa.Column("files_updated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("files_deleted", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String, nullable=False),
    )

    op.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS file_content
        USING fts5(
            file_id UNINDEXED,
            text,
            tokenize='unicode61'
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS file_content")
    op.drop_table("file_tags")
    op.drop_table("scan_log")
    op.drop_table("tags")
    op.drop_table("files")
