"""empty message

Revision ID: 48dd6f2e0784
Revises: 4fb92f3ede9e
Create Date: 2014-03-14 15:16:00.950760

"""

# revision identifiers, used by Alembic.
revision = '48dd6f2e0784'
down_revision = '4fb92f3ede9e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.rename_table('account', 'grano_account')
    op.rename_table('project', 'grano_project')
    op.rename_table('permission', 'grano_permission')
    op.rename_table('schema', 'grano_schema')
    op.rename_table('entity', 'grano_entity')
    op.rename_table('relation', 'grano_relation')
    op.rename_table('attribute', 'grano_attribute')
    op.rename_table('property', 'grano_property')
    op.rename_table('entity_schema', 'grano_entity_schema')
    

def downgrade():
    op.rename_table('grano_account', 'grano_account')
    op.rename_table('grano_project', 'project')
    op.rename_table('grano_permission', 'permission')
    op.rename_table('grano_schema', 'schema')
    op.rename_table('grano_entity', 'entity')
    op.rename_table('grano_relation', 'relation')
    op.rename_table('grano_attribute', 'attribute')
    op.rename_table('grano_property', 'property')
    op.rename_table('grano_entity_schema', 'entity_schema')
