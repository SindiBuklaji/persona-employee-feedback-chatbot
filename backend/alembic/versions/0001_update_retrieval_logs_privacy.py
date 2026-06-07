"""Update retrieval logs for privacy-conscious logging

Revision ID: 0001_update_retrieval_logs
Revises: 0c517a4306c6
Create Date: 2026-06-07 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_update_retrieval_logs'
down_revision: Union[str, None] = '0c517a4306c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove user_message_text column (linked via message_id instead)
    op.drop_column('retrieval_logs', 'user_message_text')

    # Add corpus_version for reproducibility
    op.add_column('retrieval_logs', sa.Column('corpus_version', sa.String(), nullable=False, server_default='1.0'))


def downgrade() -> None:
    # Remove corpus_version
    op.drop_column('retrieval_logs', 'corpus_version')

    # Re-add user_message_text (will be empty for new logs)
    op.add_column('retrieval_logs', sa.Column('user_message_text', sa.Text(), nullable=False, server_default=''))
