"""empty message

Revision ID: 3a3c75de71b
Revises: 48dd6f2e0784
Create Date: 2014-03-14 15:29:22.379106

"""

# revision identifiers, used by Alembic.
revision = '3a3c75de71b'
down_revision = '48dd6f2e0784'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('grano_attribute', sa.Column('datatype', sa.Unicode(), nullable=True))
    op.alter_column('grano_property', 'value', new_column_name='value_string')
    
    attribute = sa.sql.table('grano_attribute',
        sa.sql.column('datatype', sa.Unicode)
    )

    op.execute(attribute.update().values({'datatype': 'string'}))


    # leftovers:
    op.create_index('ix_grano_property_entity_id', 'grano_property', ['entity_id'], unique=False)
    op.create_index('ix_grano_property_name', 'grano_property', ['name'], unique=False)
    op.create_index('ix_grano_property_relation_id', 'grano_property', ['relation_id'], unique=False)
    op.drop_index('ix_property_entity_id', table_name='grano_property')
    op.drop_index('ix_property_name', table_name='grano_property')
    op.drop_index('ix_property_relation_id', table_name='grano_property')
    op.create_index('ix_grano_relation_schema_id', 'grano_relation', ['schema_id'], unique=False)
    op.create_index('ix_grano_relation_source_id', 'grano_relation', ['source_id'], unique=False)
    op.create_index('ix_grano_relation_target_id', 'grano_relation', ['target_id'], unique=False)
    op.drop_index('ix_relation_schema_id', table_name='grano_relation')
    op.drop_index('ix_relation_source_id', table_name='grano_relation')
    op.drop_index('ix_relation_target_id', table_name='grano_relation')


def downgrade():
    op.create_index('ix_relation_target_id', 'grano_relation', ['target_id'], unique=False)
    op.create_index('ix_relation_source_id', 'grano_relation', ['source_id'], unique=False)
    op.create_index('ix_relation_schema_id', 'grano_relation', ['schema_id'], unique=False)
    op.drop_index('ix_grano_relation_target_id', table_name='grano_relation')
    op.drop_index('ix_grano_relation_source_id', table_name='grano_relation')
    op.drop_index('ix_grano_relation_schema_id', table_name='grano_relation')
    op.create_index('ix_property_relation_id', 'grano_property', ['relation_id'], unique=False)
    op.create_index('ix_property_name', 'grano_property', ['name'], unique=False)
    op.create_index('ix_property_entity_id', 'grano_property', ['entity_id'], unique=False)
    op.drop_index('ix_grano_property_relation_id', table_name='grano_property')
    op.drop_index('ix_grano_property_name', table_name='grano_property')
    op.drop_index('ix_grano_property_entity_id', table_name='grano_property')
    op.drop_column('grano_attribute', 'datatype')

    op.alter_column('grano_property', 'value_string', new_column_name='value')

