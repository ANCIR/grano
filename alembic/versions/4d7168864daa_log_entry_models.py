"""log entry models

Revision ID: 4d7168864daa
Revises: 32a25698e4bb
Create Date: 2014-04-06 21:42:28.317694

"""

# revision identifiers, used by Alembic.
revision = '4d7168864daa'
down_revision = '32a25698e4bb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('grano_log_entry',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pipeline_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Unicode(), nullable=True),
    sa.Column('message', sa.Unicode(), nullable=True),
    sa.Column('error', sa.Unicode(), nullable=True),
    sa.Column('details', sa.Unicode(), nullable=True),
    sa.ForeignKeyConstraint(['pipeline_id'], ['grano_pipeline.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('grano_log_entry')
