import sys
import os

from app import create_app, db
from app.models.models import DailyLog, FlockBodyweight, FlockBodyweightPartition, PartitionWeight

app = create_app()

with app.app_context():
    logs_with_bw = DailyLog.query.filter_by(is_weighing_day=True).all()
    count = 0
    for log in logs_with_bw:
        # Check if already migrated
        existing = FlockBodyweight.query.filter_by(flock_id=log.flock_id, date=log.date).first()
        if not existing:
            new_bw = FlockBodyweight(
                flock_id=log.flock_id,
                date=log.date,
                body_weight_male=log.body_weight_male,
                body_weight_female=log.body_weight_female,
                uniformity_male=log.uniformity_male,
                uniformity_female=log.uniformity_female,
                standard_bw_male=log.standard_bw_male,
                standard_bw_female=log.standard_bw_female
            )
            db.session.add(new_bw)
            db.session.flush()

            # Migrate partitions
            for pw in log.partition_weights:
                new_pw = FlockBodyweightPartition(
                    bodyweight_id=new_bw.id,
                    partition_name=pw.partition_name,
                    body_weight=pw.body_weight,
                    uniformity=pw.uniformity
                )
                db.session.add(new_pw)

            count += 1

    db.session.commit()
    print(f"Migrated {count} bodyweight entries.")
