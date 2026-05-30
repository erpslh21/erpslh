"""upgrade_broiler_flock_facilities

Revision ID: b973fe46f8f4
Revises: 62227d5965c6
Create Date: 2026-05-30 07:06:25.641880

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'b973fe46f8f4'
down_revision = '62227d5965c6'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    # Stale temporary table cleanup for SQLite batch issues
    bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_broiler_daily_log"))
    bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_broiler_flock"))
    
    # 1. Defensively check and build the farm table if not exists (safeguard)
    if not inspector.has_table('farm'):
        op.create_table('farm',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('department', sa.String(length=50), server_default='Breeder', nullable=False),
            sa.PrimaryKeyConstraint('id', name='pk_farm'),
            sa.UniqueConstraint('name', name='uq_farm_name')
        )
        
    # 2. Defensively check and build the house table if not exists (safeguard)
    if not inspector.has_table('house'):
        op.create_table('house',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('farm_id', sa.Integer(), nullable=True),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.ForeignKeyConstraint(['farm_id'], ['farm.id'], name='fk_house_farm_id_farm'),
            sa.PrimaryKeyConstraint('id', name='pk_house'),
            sa.UniqueConstraint('name', name='uq_house_name')
        )
        with op.batch_alter_table('house', schema=None) as batch_op:
            batch_op.create_index('ix_house_farm_id', ['farm_id'], unique=False)

    # 3. Handle broiler_flock table alterations or creation
    if not inspector.has_table('broiler_flock'):
        op.create_table('broiler_flock',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('farm_id', sa.Integer(), nullable=False),
            sa.Column('house_id', sa.Integer(), nullable=False),
            sa.Column('farm_name', sa.String(length=100), nullable=True),
            sa.Column('house_name', sa.String(length=100), nullable=True),
            sa.Column('source', sa.String(length=100), nullable=True),
            sa.Column('breed', sa.String(length=50), nullable=True),
            sa.Column('intake_birds', sa.Integer(), nullable=False),
            sa.Column('intake_date', sa.Date(), nullable=False),
            sa.Column('arrival_weight_g', sa.Float(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('harvest_date', sa.Date(), nullable=True),
            sa.Column('harvested_birds', sa.Integer(), nullable=True),
            sa.Column('harvest_fcr', sa.Float(), nullable=True),
            sa.Column('harvest_avg_weight', sa.Float(), nullable=True),
            sa.ForeignKeyConstraint(['farm_id'], ['farm.id'], name='fk_broiler_flock_farm_id_farm'),
            sa.ForeignKeyConstraint(['house_id'], ['house.id'], name='fk_broiler_flock_house_id_house'),
            sa.PrimaryKeyConstraint('id', name='pk_broiler_flock')
        )
        with op.batch_alter_table('broiler_flock', schema=None) as batch_op:
            batch_op.create_index('ix_broiler_flock_farm_id', ['farm_id'], unique=False)
            batch_op.create_index('ix_broiler_flock_house_id', ['house_id'], unique=False)
            batch_op.create_index('ix_broiler_flock_is_active', ['is_active'], unique=False)
    else:
        # Table exists. Let's add columns defensively.
        columns = [c['name'] for c in inspector.get_columns('broiler_flock')]
        
        # Add nullable=True first for data sync
        if 'farm_id' not in columns:
            op.add_column('broiler_flock', sa.Column('farm_id', sa.Integer(), nullable=True))
        if 'house_id' not in columns:
            op.add_column('broiler_flock', sa.Column('house_id', sa.Integer(), nullable=True))
        if 'harvest_date' not in columns:
            op.add_column('broiler_flock', sa.Column('harvest_date', sa.Date(), nullable=True))
        if 'harvested_birds' not in columns:
            op.add_column('broiler_flock', sa.Column('harvested_birds', sa.Integer(), nullable=True))
        if 'harvest_fcr' not in columns:
            op.add_column('broiler_flock', sa.Column('harvest_fcr', sa.Float(), nullable=True))
        if 'harvest_avg_weight' not in columns:
            op.add_column('broiler_flock', sa.Column('harvest_avg_weight', sa.Float(), nullable=True))
        if 'is_active' not in columns:
            op.add_column('broiler_flock', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'))

        # Data sync mapping legacy name strings to database facility primary keys
        sync_and_enforce_nullable(bind, inspector)

def sync_and_enforce_nullable(bind, inspector):
    # 1. Fetch active farms to look up existing mapping
    farms_res = bind.execute(sa.text("SELECT id, name FROM farm")).fetchall()
    farm_map = {f[1].strip().lower(): f[0] for f in farms_res}

    # 2. Fetch active houses to look up existing mapping
    houses_res = bind.execute(sa.text("SELECT id, name, farm_id FROM house")).fetchall()
    house_map = {h[1].strip().lower(): (h[0], h[2]) for h in houses_res}

    # 3. Query all existing broiler flocks
    flocks = bind.execute(sa.text("SELECT id, farm_name, house_name FROM broiler_flock")).fetchall()

    for f_id, f_name, h_name in flocks:
        f_name_clean = f_name.strip() if f_name else "Default Farm"
        h_name_clean = h_name.strip() if h_name else "Default House"
        
        # Ensure Farm exists in DB
        f_key = f_name_clean.lower()
        if f_key not in farm_map:
            # Create dynamic Broiler Farm
            bind.execute(
                sa.text("INSERT INTO farm (name, department) VALUES (:name, 'Broiler')"),
                {"name": f_name_clean}
            )
            # Retrieve last inserted id
            new_farm_id = bind.execute(sa.text("SELECT id FROM farm WHERE name = :name"), {"name": f_name_clean}).scalar()
            farm_map[f_key] = new_farm_id

        farm_id = farm_map[f_key]

        # Ensure House exists in DB
        h_key = h_name_clean.lower()
        if h_key not in house_map:
            # Create dynamic House linked to Farm
            bind.execute(
                sa.text("INSERT INTO house (name, farm_id) VALUES (:name, :farm_id)"),
                {"name": h_name_clean, "farm_id": farm_id}
            )
            # Retrieve last inserted id
            new_house_id = bind.execute(sa.text("SELECT id FROM house WHERE name = :name"), {"name": h_name_clean}).scalar()
            house_map[h_key] = (new_house_id, farm_id)

        house_id, _ = house_map[h_key]

        # Update broiler flock with mapped foreign keys
        bind.execute(
            sa.text("UPDATE broiler_flock SET farm_id = :farm_id, house_id = :house_id WHERE id = :id"),
            {"farm_id": farm_id, "house_id": house_id, "id": f_id}
        )

    # If table has no rows or data sync completed, enforce default dynamic farm and house for any stray nulls
    # Before making it nullable=False, double check if we need to set a default farm/house
    farms_count = bind.execute(sa.text("SELECT COUNT(*) FROM farm")).scalar() or 0
    if farms_count == 0:
        # Create a fallback default farm and house
        bind.execute(sa.text("INSERT INTO farm (name, department) VALUES ('Farm A', 'Broiler')"))
        default_farm_id = bind.execute(sa.text("SELECT id FROM farm WHERE name = 'Farm A'")).scalar()
        bind.execute(sa.text("INSERT INTO house (name, farm_id) VALUES ('House 1', :farm_id)"), {"farm_id": default_farm_id})
        default_house_id = bind.execute(sa.text("SELECT id FROM house WHERE name = 'House 1'")).scalar()
    else:
        default_farm_id = bind.execute(sa.text("SELECT id FROM farm LIMIT 1")).scalar()
        # Find house belonging to that farm
        default_house_id = bind.execute(sa.text("SELECT id FROM house WHERE farm_id = :farm_id LIMIT 1"), {"farm_id": default_farm_id}).scalar()
        if not default_house_id:
            # Create a house for it
            bind.execute(sa.text("INSERT INTO house (name, farm_id) VALUES ('House 1', :farm_id)"), {"farm_id": default_farm_id})
            default_house_id = bind.execute(sa.text("SELECT id FROM house WHERE farm_id = :farm_id LIMIT 1"), {"farm_id": default_farm_id}).scalar()

    # Fill any null values left before adding nullable=False constraint
    bind.execute(
        sa.text("UPDATE broiler_flock SET farm_id = :default_farm_id WHERE farm_id IS NULL"),
        {"default_farm_id": default_farm_id}
    )
    bind.execute(
        sa.text("UPDATE broiler_flock SET house_id = :default_house_id WHERE house_id IS NULL"),
        {"default_house_id": default_house_id}
    )

    # Now safely enforce NOT NULL constraints, indexes and foreign keys using Alembic Batch alter
    with op.batch_alter_table('broiler_flock', schema=None) as batch_op:
        batch_op.alter_column('farm_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('house_id', existing_type=sa.Integer(), nullable=False)
        
        # Check if indexes exist before adding
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('broiler_flock')]
        if 'ix_broiler_flock_farm_id' not in existing_indexes:
            batch_op.create_index('ix_broiler_flock_farm_id', ['farm_id'], unique=False)
        if 'ix_broiler_flock_house_id' not in existing_indexes:
            batch_op.create_index('ix_broiler_flock_house_id', ['house_id'], unique=False)
        if 'ix_broiler_flock_is_active' not in existing_indexes:
            batch_op.create_index('ix_broiler_flock_is_active', ['is_active'], unique=False)

        # Check if foreign keys exist before adding
        fk_names = [fk['name'] for fk in inspector.get_foreign_keys('broiler_flock')]
        if not any(name and 'fk_broiler_flock_farm_id' in name.lower() for name in fk_names):
            batch_op.create_foreign_key('fk_broiler_flock_farm_id_farm', 'farm', ['farm_id'], ['id'])
        if not any(name and 'fk_broiler_flock_house_id' in name.lower() for name in fk_names):
            batch_op.create_foreign_key('fk_broiler_flock_house_id_house', 'house', ['house_id'], ['id'])

def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    if inspector.has_table('broiler_flock'):
        with op.batch_alter_table('broiler_flock', schema=None) as batch_op:
            batch_op.drop_index('ix_broiler_flock_is_active')
            batch_op.drop_index('ix_broiler_flock_house_id')
            batch_op.drop_index('ix_broiler_flock_farm_id')
            batch_op.drop_constraint('fk_broiler_flock_house_id_house', type_='foreignkey')
            batch_op.drop_constraint('fk_broiler_flock_farm_id_farm', type_='foreignkey')
            batch_op.drop_column('harvest_avg_weight')
            batch_op.drop_column('harvest_fcr')
            batch_op.drop_column('harvested_birds')
            batch_op.drop_column('harvest_date')
            batch_op.drop_column('house_id')
            batch_op.drop_column('farm_id')
