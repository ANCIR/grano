"""remove status again

Revision ID: 59d7b4f94cdf
Revises: 5143617349b9
Create Date: 2014-09-11 20:28:20.938462

"""

# revision identifiers, used by Alembic.
revision = '59d7b4f94cdf'
down_revision = '5143617349b9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column(u'grano_entity', 'status')


def downgrade():
    op.add_column(u'grano_entity', sa.Column('status', sa.INTEGER(), nullable=True))
