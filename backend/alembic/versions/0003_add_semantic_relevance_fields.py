"""Add semantic relevance classification fields to messages table."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_add_semantic_relevance'
down_revision = '0002_add_off_topic_detection'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to messages table
    op.add_column('messages', sa.Column('relevance_label', sa.String(), nullable=True))
    op.add_column('messages', sa.Column('relevance_confidence', sa.Float(), nullable=True))
    op.add_column('messages', sa.Column('is_valid_turn', sa.Boolean(), nullable=True))
    op.add_column('messages', sa.Column('safety_concern', sa.Boolean(), server_default='0', nullable=False))


def downgrade():
    # Remove new columns
    op.drop_column('messages', 'safety_concern')
    op.drop_column('messages', 'is_valid_turn')
    op.drop_column('messages', 'relevance_confidence')
    op.drop_column('messages', 'relevance_label')
