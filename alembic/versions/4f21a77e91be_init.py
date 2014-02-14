"""init

Revision ID: 4f21a77e91be
Revises: None
Create Date: 2014-02-13 17:05:34.953371

"""

# revision identifiers, used by Alembic.
revision = '4f21a77e91be'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('relation',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('schema_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('source_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('target_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['schema_id'], [u'schema.id'], name=u'relation_schema_id_fkey'),
    sa.ForeignKeyConstraint(['source_id'], [u'entity.id'], name=u'relation_source_id_fkey'),
    sa.ForeignKeyConstraint(['target_id'], [u'entity.id'], name=u'relation_target_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'relation_pkey')
    )
    op.create_table('account',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), server_default="nextval('account_id_seq'::regclass)", nullable=False),
    sa.Column('github_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('login', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('api_key', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'account_pkey')
    )
    op.create_table('entity',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('same_as', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['same_as'], [u'entity.id'], name=u'entity_same_as_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'entity_pkey')
    )
    op.create_table('property',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), server_default="nextval('property_id_seq'::regclass)", nullable=False),
    sa.Column('schema_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('value', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('source_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('obj', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('entity_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relation_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], [u'entity.id'], name=u'property_entity_id_fkey'),
    sa.ForeignKeyConstraint(['relation_id'], [u'relation.id'], name=u'property_relation_id_fkey'),
    sa.ForeignKeyConstraint(['schema_id'], [u'schema.id'], name=u'property_schema_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'property_pkey')
    )
    op.create_table('entity_schema',
    sa.Column('entity_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('schema_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], [u'entity.id'], name=u'entity_schema_entity_id_fkey'),
    sa.ForeignKeyConstraint(['schema_id'], [u'schema.id'], name=u'entity_schema_schema_id_fkey')
    )
    op.create_table('attribute',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), server_default="nextval('attribute_id_seq'::regclass)", nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('label', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('hidden', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('schema_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['schema_id'], [u'schema.id'], name=u'attribute_schema_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'attribute_pkey')
    )
    op.create_table('schema',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), server_default="nextval('schema_id_seq'::regclass)", nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('label', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('label_in', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('label_out', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('obj', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('hidden', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'schema_pkey')
    )


def downgrade():
    op.drop_table('schema')
    op.drop_table('attribute')
    op.drop_table('entity_schema')
    op.drop_table('property')
    op.drop_table('entity')
    op.drop_table('account')
    op.drop_table('relation')
