"""single schema entity

Revision ID: 1b1b7e728dc4
Revises: 3f0a4c96f763
Create Date: 2014-09-16 10:15:16.427774

"""

# revision identifiers, used by Alembic.
revision = '1b1b7e728dc4'
down_revision = '3f0a4c96f763'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.drop_table('grano_entity_schema')
    op.add_column('grano_entity', sa.Column('schema_id', sa.Integer(), nullable=True))
    op.create_index('ix_grano_entity_schema_id', 'grano_entity', ['schema_id'], unique=False)
    op.drop_column('grano_property', 'schema_id')
    

def downgrade():
    op.add_column('grano_property', sa.Column('schema_id', sa.INTEGER(), nullable=True))
    op.drop_index('ix_grano_entity_schema_id', table_name='grano_entity')
    op.drop_column('grano_entity', 'schema_id')
    
    op.create_table('grano_entity_schema',
    sa.Column('entity_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('schema_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], [u'grano_entity.id'], name=u'entity_schema_entity_id_fkey'),
    sa.ForeignKeyConstraint(['schema_id'], [u'grano_schema.id'], name=u'entity_schema_schema_id_fkey')
    )
    
