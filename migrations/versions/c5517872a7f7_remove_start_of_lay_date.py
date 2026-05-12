"""Remove start of lay date

Revision ID: c5517872a7f7
Revises: 33de47d14183
Create Date: 2026-05-03 03:18:14.003806

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'c5517872a7f7'
down_revision = '33de47d14183'
branch_labels = None
depends_on = None

def has_column(table_name, column_name):
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    if not inspector.has_table(table_name):
        return False
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    if has_column('flock', 'start_of_lay_date'):
        with op.batch_alter_table('flock', schema=None) as batch_op:
            batch_op.drop_column('start_of_lay_date')

def downgrade():
    if not has_column('flock', 'start_of_lay_date'):
        with op.batch_alter_table('flock', schema=None) as batch_op:
            batch_op.add_column(sa.Column('start_of_lay_date', sa.Date(), nullable=True))
