"""file properties

Revision ID: 3ab60d7d74a1
Revises: 5143617349b9
Create Date: 2014-07-25 15:49:46.369755

"""

revision = '3ab60d7d74a1'
down_revision = '5143617349b9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('grano_property', sa.Column('value_file_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('grano_property', 'value_file_id')
