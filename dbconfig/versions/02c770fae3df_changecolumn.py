"""changecolumn

Revision ID: 02c770fae3df
Revises: 2e38c0550fc2
Create Date: 2021-12-23 19:22:50.360512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02c770fae3df'
down_revision = '2e38c0550fc2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('datawindow', sa.Column('date', sa.String(length=10), server_default='', nullable=False))
    op.add_column('datawindow', sa.Column('firstTs', sa.Integer(), server_default='0', nullable=False))
    op.add_column('datawindow', sa.Column('highestTs', sa.Integer(), server_default='0', nullable=False))
    op.add_column('datawindow', sa.Column('lastTs', sa.Integer(), server_default='0', nullable=False))
    op.add_column('datawindow', sa.Column('startTs', sa.Integer(), server_default='0', nullable=False))
    op.drop_column('datawindow', 'endIdx')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('datawindow', sa.Column('endIdx', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.drop_column('datawindow', 'startTs')
    op.drop_column('datawindow', 'lastTs')
    op.drop_column('datawindow', 'highestTs')
    op.drop_column('datawindow', 'firstTs')
    op.drop_column('datawindow', 'date')
    # ### end Alembic commands ###
