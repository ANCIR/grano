"""Add value_datetime_precision to Property

Revision ID: b64496669cd
Revises: 1b1b7e728dc4
Create Date: 2014-10-14 15:58:37.251624

"""

# revision identifiers, used by Alembic.
revision = 'b64496669cd'
down_revision = '1b1b7e728dc4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'grano_property', sa.Column('value_datetime_precision', sa.Enum('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', native_enum=False), nullable=True))


def downgrade():
    op.drop_column(u'grano_property', 'value_datetime_precision')
