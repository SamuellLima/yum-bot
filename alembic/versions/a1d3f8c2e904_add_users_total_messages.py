"""add users total_messages

Revision ID: a1d3f8c2e904
Revises: 102edc087b1a
Create Date: 2026-09-04 17:13:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1d3f8c2e904'
down_revision: Union[str, Sequence[str], None] = '102edc087b1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('total_messages', sa.Integer(), server_default=sa.text('0'), nullable=False),
    )
    op.execute(sa.text("UPDATE users SET total_messages = count_messages"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'total_messages')
