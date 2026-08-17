"""sync issue status enum values

Revision ID: 89801ea2cc5f
Revises: 63aaa26afb29
Create Date: 2026-08-17 11:11:11.684845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89801ea2cc5f'
down_revision: Union[str, Sequence[str], None] = '63aaa26afb29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE issue_status ADD VALUE IF NOT EXISTS 'BACKLOG'")
    op.execute("ALTER TYPE issue_status ADD VALUE IF NOT EXISTS 'CODE_REVIEW'")
    op.execute("ALTER TYPE issue_status ADD VALUE IF NOT EXISTS 'TESTING'")
    op.execute("ALTER TYPE issue_status ADD VALUE IF NOT EXISTS 'UAT'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly.
    # Leave downgrade empty unless a full enum recreation is required.
    pass