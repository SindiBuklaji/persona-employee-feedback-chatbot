"""Add off-topic detection tracking to messages

Revision ID: 0002_add_off_topic_detection
Revises: 0001_update_retrieval_logs
Create Date: 2026-06-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_add_off_topic_detection'
down_revision: Union[str, None] = '0001_update_retrieval_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('messages', sa.Column('is_off_topic_redirect', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('messages', sa.Column('off_topic_reason', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('messages', 'off_topic_reason')
    op.drop_column('messages', 'is_off_topic_redirect')
