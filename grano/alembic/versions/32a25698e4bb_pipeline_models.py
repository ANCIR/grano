"""pipeline models

Revision ID: 32a25698e4bb
Revises: 52f4346513a8
Create Date: 2014-04-06 21:40:28.224450

"""

# revision identifiers, used by Alembic.
revision = '32a25698e4bb'
down_revision = '52f4346513a8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('grano_pipeline',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('operation', sa.Unicode(), nullable=True),
    sa.Column('status', sa.Unicode(), nullable=True),
    sa.Column('percent_complete', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('config', sa.Unicode(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['grano_account.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['grano_project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('grano_pipeline')
    
