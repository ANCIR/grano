"""add image config relation to attribute

Revision ID: 5c5d246934d
Revises: 2bb0519ed7f3
Create Date: 2014-07-15 16:30:15.771036

"""

# revision identifiers, used by Alembic.
revision = '5c5d246934d'
down_revision = '2bb0519ed7f3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('grano_attribute', sa.Column('image_config_id', sa.Integer(), sa.ForeignKey('grano_imageconfig.id'), nullable=True))


def downgrade():
    op.drop_column('grano_attribute', 'image_config_id')
