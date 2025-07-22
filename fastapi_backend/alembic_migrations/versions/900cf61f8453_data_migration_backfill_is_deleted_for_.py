"""data migration: backfill is_deleted for xhs_notes

Revision ID: 900cf61f8453
Revises: 492724b8b6c3
Create Date: 2025-07-22 08:09:20.576511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '900cf61f8453'
down_revision: Union[str, None] = '492724b8b6c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Backfill is_deleted to False for existing rows in xhs_notes table.
    """
    op.execute(
        """
        UPDATE xhs_notes
        SET is_deleted = FALSE
        WHERE is_deleted IS NULL;
        """
    )


def downgrade() -> None:
    """
    This data migration is not easily reversible. Pass.
    """
    pass
