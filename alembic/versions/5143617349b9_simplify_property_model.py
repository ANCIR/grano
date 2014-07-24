"""simplify property model

Revision ID: 5143617349b9
Revises: 992aea84727
Create Date: 2014-07-22 14:15:07.069896

"""

# revision identifiers, used by Alembic.
revision = '5143617349b9'
down_revision = '25bb7c68b5fa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('grano_property', 'obj')


def downgrade():
    op.add_column('grano_property',
                  sa.Column('obj', sa.VARCHAR(length=20), nullable=True))
