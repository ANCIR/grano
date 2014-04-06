"""introduce project class

Revision ID: 40941ab93ba
Revises: 4f21a77e91be
Create Date: 2014-02-13 17:14:57.212052

"""

# revision identifiers, used by Alembic.
revision = '40941ab93ba'
down_revision = '4f21a77e91be'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('project',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.Unicode(), nullable=True),
    sa.Column('label', sa.Unicode(), nullable=True),
    sa.Column('settings', sa.Unicode(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('project')
    
