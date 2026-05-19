import sys
import os

from sqlalchemy import text
from app import create_app, db
from app.models.models import FlockBodyweight, FlockBodyweightPartition

app = create_app()

with app.app_context():
    # Use raw SQL to fetch legacy fields from daily_log to avoid ORM errors
    # since these columns might have been removed from the DailyLog model.
    query = text('''
        SELECT id, flock_id, date, body_weight_male, body_weight_female,
               uniformity_male, uniformity_female, standard_bw_male, standard_bw_female
        FROM daily_log
        WHERE is_weighing_day = 1 OR is_weighing_day = true
    ''')
    logs_with_bw = db.session.execute(query).fetchall()
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

            # Migrate partitions using raw SQL
            pw_query = text('''
                SELECT partition_name, body_weight, uniformity
                FROM partition_weight
                WHERE log_id = :log_id
            ''')
            partitions = db.session.execute(pw_query, {'log_id': log.id}).fetchall()

            for pw in partitions:
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
