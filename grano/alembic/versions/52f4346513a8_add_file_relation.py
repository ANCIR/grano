"""add file relation

Revision ID: 52f4346513a8
Revises: d7067cd4169
Create Date: 2014-04-02 16:33:16.710455

"""

# revision identifiers, used by Alembic.
revision = '52f4346513a8'
down_revision = 'd7067cd4169'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('grano_file',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.Unicode(), nullable=True),
        sa.Column('mime_type', sa.Unicode(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('data', sa.LargeBinary(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['grano_account.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['grano_project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    #op.drop_table('role')


def downgrade():
    op.drop_table('grano_file')
