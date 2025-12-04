"""add_google_chat_action_type

Revision ID: c6b8b03c1711
Revises: af475f2563b3
Create Date: 2025-12-04 00:37:41.499890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6b8b03c1711'
down_revision: Union[str, None] = 'af475f2563b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add GOOGLE_CHAT to actiontype enum
    op.execute("ALTER TYPE actiontype ADD VALUE 'GOOGLE_CHAT'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values
    # This would require recreating the enum type
    pass
