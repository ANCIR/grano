"""pipeline model improved

Revision ID: 2372546f7078
Revises: 4d7168864daa
Create Date: 2014-04-07 22:05:01.431021

"""

# revision identifiers, used by Alembic.
revision = '2372546f7078'
down_revision = '4d7168864daa'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('grano_pipeline', sa.Column('label', sa.Unicode(), nullable=True))
    op.drop_column('grano_log_entry', 'level')
    op.add_column('grano_log_entry', sa.Column('level', sa.Integer(), nullable=True))
    

def downgrade():
    op.drop_column('grano_pipeline', 'title')
    
