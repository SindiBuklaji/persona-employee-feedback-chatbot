"""Update perception items to better measure persona differences."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_update_perception_items'
down_revision = '0003_add_semantic_relevance'
branch_labels = None
depends_on = None


def upgrade():
    # Add new warmth item
    op.add_column('questionnaire_responses', sa.Column('perc_warm_comfortable', sa.Integer(), nullable=True))

    # Add new structured/direct items
    op.add_column('questionnaire_responses', sa.Column('perc_struct_direct', sa.Integer(), nullable=True))
    op.add_column('questionnaire_responses', sa.Column('perc_struct_professional', sa.Integer(), nullable=True))
    op.add_column('questionnaire_responses', sa.Column('perc_struct_task_focused', sa.Integer(), nullable=True))


def downgrade():
    # Remove new columns
    op.drop_column('questionnaire_responses', 'perc_struct_task_focused')
    op.drop_column('questionnaire_responses', 'perc_struct_professional')
    op.drop_column('questionnaire_responses', 'perc_struct_direct')
    op.drop_column('questionnaire_responses', 'perc_warm_comfortable')
