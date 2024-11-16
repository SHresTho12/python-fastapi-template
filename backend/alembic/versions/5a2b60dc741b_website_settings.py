"""website settings

Revision ID: 5a2b60dc741b
Revises: fa6a33a07129
Create Date: 2024-09-03 05:45:05.126672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a2b60dc741b'
down_revision = 'fa6a33a07129'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('website_settings',
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('settings_data', sa.JSON(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('updated_by_id', sa.Integer(), nullable=True),
    sa.Column('deleted_by_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['deleted_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_website_settings_id'), 'website_settings', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_website_settings_id'), table_name='website_settings')
    op.drop_table('website_settings')
    # ### end Alembic commands ###
