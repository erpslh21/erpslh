"""defensive_add_department

Revision ID: 62227d5965c6
Revises: 5624481a4593
Create Date: 2026-05-30 06:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '62227d5965c6'
down_revision = '5624481a4593'
branch_labels = None
depends_on = None

def upgrade():
    # Defensively check if 'department' column exists in 'farm' table
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    # Check if 'farm' table exists first
    if inspector.has_table('farm'):
        columns = [c['name'] for c in inspector.get_columns('farm')]
        if 'department' not in columns:
            with op.batch_alter_table('farm', schema=None) as batch_op:
                batch_op.add_column(sa.Column('department', sa.String(length=50), server_default='Breeder', nullable=False))

def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    if inspector.has_table('farm'):
        columns = [c['name'] for c in inspector.get_columns('farm')]
        if 'department' in columns:
            with op.batch_alter_table('farm', schema=None) as batch_op:
                batch_op.drop_column('department')
