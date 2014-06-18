"""Add status field to Entity

Revision ID: 383da0877c75
Revises: 2372546f7078
Create Date: 2014-05-27 15:13:07.953084

"""

# revision identifiers, used by Alembic.
revision = '383da0877c75'
down_revision = '2372546f7078'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('grano_entity', sa.Column('status', sa.Integer))


def downgrade():
    op.drop_column('grano_entity', 'status')
