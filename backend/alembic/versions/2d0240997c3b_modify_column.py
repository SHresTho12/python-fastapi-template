"""modify column

Revision ID: 2d0240997c3b
Revises: eb3427015879
Create Date: 2024-09-03 08:05:57.101864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d0240997c3b'
down_revision = 'eb3427015879'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('website_settings', sa.Column('tools', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('website_settings', 'tools')
    # ### end Alembic commands ###
