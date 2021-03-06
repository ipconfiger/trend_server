"""upcolumn

Revision ID: 2e38c0550fc2
Revises: b17f67e24440
Create Date: 2021-12-20 20:01:05.415859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e38c0550fc2'
down_revision = 'b17f67e24440'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'datawindow', ['id'])
    op.create_unique_constraint(None, 'executionresult', ['id'])
    op.add_column('executiontask', sa.Column('product', sa.String(length=36), nullable=False))
    op.create_unique_constraint(None, 'executiontask', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'executiontask', type_='unique')
    op.drop_column('executiontask', 'product')
    op.drop_constraint(None, 'executionresult', type_='unique')
    op.drop_constraint(None, 'datawindow', type_='unique')
    # ### end Alembic commands ###
