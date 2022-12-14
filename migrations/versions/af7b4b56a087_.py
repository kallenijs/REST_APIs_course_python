"""empty message

Revision ID: af7b4b56a087
Revises: c50a6ffefdf8
Create Date: 2022-10-27 14:16:33.541274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af7b4b56a087'
down_revision = 'c50a6ffefdf8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_email', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'users', ['user_email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'user_email')
    # ### end Alembic commands ###
