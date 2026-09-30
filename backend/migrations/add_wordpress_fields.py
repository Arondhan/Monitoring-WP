"""
Миграция: добавление WordPress-полей в таблицу domains.
Используется Uptime Checker для мониторинга WP-сайтов (отдельно от автопостера).
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "domains",
        sa.Column("is_wordpress", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "domains",
        sa.Column("last_post_date", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "domains",
        sa.Column("last_post_title", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "domains",
        sa.Column("last_post_checked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "domains",
        sa.Column("wordpress_version", sa.String(length=50), nullable=True),
    )


def downgrade():
    op.drop_column("domains", "wordpress_version")
    op.drop_column("domains", "last_post_checked_at")
    op.drop_column("domains", "last_post_title")
    op.drop_column("domains", "last_post_date")
    op.drop_column("domains", "is_wordpress")
