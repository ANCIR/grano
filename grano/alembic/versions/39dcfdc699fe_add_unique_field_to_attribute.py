"""Add unique field to attribute

Revision ID: 39dcfdc699fe
Revises: b64496669cd
Create Date: 2014-11-20 17:26:28.680219

"""

# revision identifiers, used by Alembic.
revision = '39dcfdc699fe'
down_revision = 'b64496669cd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'grano_attribute', sa.Column('unique', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column(u'grano_attribute', 'unique')
