"""add schema inheritance

Revision ID: 3f0a4c96f763
Revises: 38c7982f4160
Create Date: 2014-09-14 21:47:02.098699

"""

# revision identifiers, used by Alembic.
revision = '3f0a4c96f763'
down_revision = '38c7982f4160'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'grano_attribute', sa.Column('inherited', sa.Boolean(), nullable=True))
    op.add_column(u'grano_schema', sa.Column('parent_id', sa.Integer(), nullable=True))
    

def downgrade():
    op.drop_column(u'grano_schema', 'parent_id')
    op.drop_column(u'grano_attribute', 'inherited')
