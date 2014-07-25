"""add file foreign key to property

Revision ID: 25bb7c68b5fa
Revises: 383da0877c75
Create Date: 2014-07-14 15:09:01.525766

"""

# revision identifiers, used by Alembic.
revision = '25bb7c68b5fa'
down_revision = '992aea84727'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('grano_property', sa.Column('value_file_id', sa.Integer(), sa.ForeignKey('grano_file.id'), nullable=True))


def downgrade():
    op.drop_column('grano_property', 'value_file_id')
