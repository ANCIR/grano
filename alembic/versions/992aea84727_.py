"""Add metadata to schema

Revision ID: 992aea84727
Revises: 383da0877c75
Create Date: 2014-07-09 14:27:28.657758

"""

# revision identifiers, used by Alembic.
revision = '992aea84727'
down_revision = '383da0877c75'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('grano_schema', 'label_in')
    op.drop_column('grano_schema', 'label_out')
    op.add_column('grano_schema', sa.Column('meta', sa.Unicode(),
                                            nullable=True))


def downgrade():
    op.drop_column('grano_schema', 'meta')
