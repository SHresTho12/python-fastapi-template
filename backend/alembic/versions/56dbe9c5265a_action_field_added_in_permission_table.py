"""action field added in permission table

Revision ID: 56dbe9c5265a
Revises: 7b69060ff190
Create Date: 2024-09-05 06:48:35.836835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56dbe9c5265a'
down_revision = '7b69060ff190'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('permissions', sa.Column('action', sa.JSON(), nullable=True))
    op.drop_column('permissions', 'create')
    op.drop_column('permissions', 'delete')
    op.drop_column('permissions', 'view')
    op.drop_column('permissions', 'edit')
    op.drop_column('permissions', 'list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('permissions', sa.Column('list', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('permissions', sa.Column('edit', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('permissions', sa.Column('view', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('permissions', sa.Column('delete', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('permissions', sa.Column('create', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('permissions', 'action')
    # ### end Alembic commands ###
