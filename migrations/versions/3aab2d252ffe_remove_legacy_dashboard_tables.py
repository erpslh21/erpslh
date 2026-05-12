"""Remove legacy dashboard tables

Revision ID: 3aab2d252ffe
Revises: 44c2f925aa84
Create Date: 2026-03-17 05:37:19.175509

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '3aab2d252ffe'
down_revision = '44c2f925aa84'
branch_labels = None
depends_on = None

def upgrade():
    # Safely drop legacy dashboard tables if they exist
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'dashboard_widget' in tables:
        op.drop_table('dashboard_widget')
    if 'dashboard_layout' in tables:
        op.drop_table('dashboard_layout')
    if 'custom_dashboard' in tables:
        op.drop_table('custom_dashboard')
    if 'dashboard' in tables:
        op.drop_table('dashboard')

def downgrade():
    pass
