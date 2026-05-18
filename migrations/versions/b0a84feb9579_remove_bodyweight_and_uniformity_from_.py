"""Remove bodyweight and uniformity from DailyLog

Revision ID: b0a84feb9579
Revises: 3463bd0c4ada
Create Date: 2026-05-18 07:11:19.043033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0a84feb9579'
down_revision = '3463bd0c4ada'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('daily_log', schema=None) as batch_op:
        batch_op.drop_column('body_weight_male')
        batch_op.drop_column('body_weight_female')
        batch_op.drop_column('uniformity_male')
        batch_op.drop_column('uniformity_female')
        batch_op.drop_column('bw_male_p1')
        batch_op.drop_column('bw_male_p2')
        batch_op.drop_column('unif_male_p1')
        batch_op.drop_column('unif_male_p2')
        batch_op.drop_column('bw_female_p1')
        batch_op.drop_column('bw_female_p2')
        batch_op.drop_column('bw_female_p3')
        batch_op.drop_column('bw_female_p4')
        batch_op.drop_column('unif_female_p1')
        batch_op.drop_column('unif_female_p2')
        batch_op.drop_column('unif_female_p3')
        batch_op.drop_column('unif_female_p4')
        batch_op.drop_column('standard_bw_male')
        batch_op.drop_column('standard_bw_female')

def downgrade():
    with op.batch_alter_table('daily_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unif_female_p3', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('bw_female_p4', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('bw_female_p2', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('bw_female_p3', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('body_weight_female', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('bw_male_p1', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('bw_female_p1', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('uniformity_female', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('unif_male_p1', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('bw_male_p2', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('uniformity_male', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('unif_male_p2', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('unif_female_p1', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('unif_female_p4', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('unif_female_p2', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('body_weight_male', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('standard_bw_male', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('standard_bw_female', sa.INTEGER(), nullable=True))
