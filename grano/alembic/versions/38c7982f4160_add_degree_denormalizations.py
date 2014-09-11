"""add degree denormalizations

Revision ID: 38c7982f4160
Revises: 59d7b4f94cdf
Create Date: 2014-09-11 20:32:37.987989

"""

# revision identifiers, used by Alembic.
revision = '38c7982f4160'
down_revision = '59d7b4f94cdf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'grano_entity', sa.Column('degree_in', sa.Integer(), nullable=True))
    op.add_column(u'grano_entity', sa.Column('degree_out', sa.Integer(), nullable=True))
    op.add_column(u'grano_entity', sa.Column('degree', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column(u'grano_entity', 'degree_out')
    op.drop_column(u'grano_entity', 'degree_in')
    op.drop_column(u'grano_entity', 'degree')
    
