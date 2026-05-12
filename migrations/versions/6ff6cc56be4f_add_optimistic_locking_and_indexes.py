"""Add optimistic locking and indexes

Revision ID: 6ff6cc56be4f
Revises: 3aab2d252ffe
Create Date: 2026-03-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '6ff6cc56be4f'
down_revision = '3aab2d252ffe'
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
    tables_to_add_version = [
        'clinical_note', 'daily_log', 'daily_log_photo', 'farm', 'feed_code',
        'floating_note', 'flock_grading', 'hatchability', 'house', 'imported_weekly_benchmark',
        'inventory_item', 'medication', 'partition_weight', 'sampling_event', 'standard',
        'ui_element', 'user', 'vaccine'
    ]

    for table in tables_to_add_version:
        if not has_column(table, 'version'):
            with op.batch_alter_table(table, schema=None) as batch_op:
                batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))

def downgrade():
    pass
