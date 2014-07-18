"""image config

Revision ID: 2bb0519ed7f3
Revises: 25bb7c68b5fa
Create Date: 2014-07-15 16:03:06.798332

"""

# revision identifiers, used by Alembic.
revision = '2bb0519ed7f3'
down_revision = '25bb7c68b5fa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('grano_imageconfig',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(), nullable=True),
    sa.Column('label', sa.Unicode(), nullable=True),
    sa.Column('description', sa.Unicode(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['grano_project.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'project_id')
    )
    op.add_column('grano_file', sa.Column('image_config_id', sa.Integer(), sa.ForeignKey('grano_imageconfig.id'), nullable=True))
    op.add_column('grano_attribute', sa.Column('image_config_id', sa.Integer(), sa.ForeignKey('grano_imageconfig.id'), nullable=True))


def downgrade():
    op.drop_column('grano_file', 'image_config_id')
    op.drop_column('grano_attribute', 'image_config_id')
    op.drop_table('grano_imageconfig')
