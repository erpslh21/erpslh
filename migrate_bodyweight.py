import sys
import os
from datetime import datetime

from sqlalchemy import text
from app import create_app, db
from app.models.models import FlockBodyweight, FlockBodyweightPartition

app = create_app()

with app.app_context():
    query_logs = text("""
        SELECT id, flock_id, date, body_weight_male, body_weight_female,
               uniformity_male, uniformity_female, standard_bw_male, standard_bw_female
        FROM daily_log
        WHERE is_weighing_day = 1 OR is_weighing_day = true
    """)
    logs_with_bw = db.session.execute(query_logs).mappings().fetchall()

    count = 0
    for log in logs_with_bw:
        # Check if already migrated
        log_date = log['date']
        if isinstance(log_date, str):
            try:
                log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
            except ValueError:
                pass

        existing = FlockBodyweight.query.filter_by(flock_id=log['flock_id'], date=log_date).first()
        if not existing:
            new_bw = FlockBodyweight(
                flock_id=log['flock_id'],
                date=log_date,
                body_weight_male=log['body_weight_male'],
                body_weight_female=log['body_weight_female'],
                uniformity_male=log['uniformity_male'],
                uniformity_female=log['uniformity_female'],
                standard_bw_male=log['standard_bw_male'],
                standard_bw_female=log['standard_bw_female']
            )
            db.session.add(new_bw)
            db.session.flush()

            # Migrate partitions
            query_partitions = text("""
                SELECT partition_name, body_weight, uniformity
                FROM partition_weight
                WHERE log_id = :log_id
            """)
            partitions = db.session.execute(query_partitions, {'log_id': log['id']}).mappings().fetchall()

            for pw in partitions:
                new_pw = FlockBodyweightPartition(
                    bodyweight_id=new_bw.id,
                    partition_name=pw['partition_name'],
                    body_weight=pw['body_weight'],
                    uniformity=pw['uniformity']
                )
                db.session.add(new_pw)

            count += 1

    db.session.commit()
    print(f"Migrated {count} bodyweight entries.")
