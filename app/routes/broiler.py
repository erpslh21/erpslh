from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.models import BroilerFlock, BroilerDailyLog
from app.database import db
from metrics import calculate_broiler_metrics
from datetime import datetime

broiler_bp = Blueprint('broiler', __name__, url_prefix='/broiler')

@broiler_bp.route('/dashboard')
def dashboard():
    from app.models.models import Farm
    active_flocks = BroilerFlock.query.filter_by(is_active=True).all()
    harvested_flocks = BroilerFlock.query.filter_by(is_active=False).order_by(BroilerFlock.harvest_date.desc()).all()
    
    # Retrieve all farms with department='Broiler' (or all as fallback)
    farms = Farm.query.filter(Farm.department.ilike('broiler')).all()
    if not farms:
        farms = Farm.query.all()
        
    return render_template(
        'broiler/broiler_dashboard.html',
        active_flocks=active_flocks,
        harvested_flocks=harvested_flocks,
        farms=farms,
        today=datetime.utcnow().date()
    )

@broiler_bp.route('/new_flock', methods=['GET', 'POST'])
def new_flock():
    from app.models.models import Farm, House
    if request.method == 'POST':
        farm_id = request.form.get('farm_id')
        house_id = request.form.get('house_id')
        source = request.form.get('source')
        breed = request.form.get('breed')
        intake_birds = int(request.form.get('intake_birds', 0))
        intake_date_str = request.form.get('intake_date')
        arrival_weight_g = float(request.form.get('arrival_weight_g', 0.0))

        intake_date = datetime.strptime(intake_date_str, '%Y-%m-%d').date() if intake_date_str else datetime.utcnow().date()

        farm = Farm.query.get_or_404(farm_id)
        house = House.query.get_or_404(house_id)

        flock = BroilerFlock(
            farm_id=farm.id,
            house_id=house.id,
            farm_name=farm.name,
            house_name=house.name,
            source=source,
            breed=breed,
            intake_birds=intake_birds,
            intake_date=intake_date,
            arrival_weight_g=arrival_weight_g,
            is_active=True
        )
        db.session.add(flock)
        db.session.commit()
        flash('Broiler flock created successfully.', 'success')
        return redirect(url_for('broiler.dashboard'))

    farms = Farm.query.filter(Farm.department.ilike('broiler')).all()
    if not farms:
        farms = Farm.query.all()
    return render_template('broiler/broiler_new_flock.html', farms=farms)

@broiler_bp.route('/flock/<int:flock_id>/harvest', methods=['POST'])
def harvest_flock(flock_id):
    flock = BroilerFlock.query.get_or_404(flock_id)
    
    harvest_date_str = request.form.get('harvest_date')
    try:
        harvested_birds = int(request.form.get('harvested_birds', 0))
    except (ValueError, TypeError):
        harvested_birds = 0
        
    try:
        harvest_fcr = float(request.form.get('harvest_fcr', 0.0))
    except (ValueError, TypeError):
        harvest_fcr = 0.0
        
    try:
        harvest_avg_weight = float(request.form.get('harvest_avg_weight', 0.0))
    except (ValueError, TypeError):
        harvest_avg_weight = 0.0

    harvest_date = datetime.strptime(harvest_date_str, '%Y-%m-%d').date() if harvest_date_str else datetime.utcnow().date()

    flock.is_active = False
    flock.harvest_date = harvest_date
    flock.harvested_birds = harvested_birds
    flock.harvest_fcr = harvest_fcr
    flock.harvest_avg_weight = harvest_avg_weight

    db.session.commit()
    flash(f"Broiler flock {flock.farm_name} - {flock.house_name} harvested successfully.", "success")
    return redirect(url_for('broiler.dashboard'))

@broiler_bp.route('/flock/<int:flock_id>')
def flock_detail(flock_id):
    flock = BroilerFlock.query.get_or_404(flock_id)

    active_flocks = BroilerFlock.query.filter_by(is_active=True).all()
    from app.utils import natural_sort_key
    if active_flocks:
        active_flocks.sort(key=lambda x: natural_sort_key(f"{x.farm_name} - {x.house_name}"))

    # Fetch calculated metrics for display
    metrics = calculate_broiler_metrics(flock.id)

    intake_birds = flock.intake_birds or 0
    # Prepare JSON-serializable lists for Chart.js
    chart_data = {
        'days': [m['day_number'] for m in metrics],
        'actual_fcr': [m['cumulative_fcr'] for m in metrics],
        'standard_fcr': [m.get('standard_fcr') or 0.0 for m in metrics],
        'body_weights': [m['body_weight_g'] for m in metrics],
        'bodyweight_standard': [m.get('standard_body_weight_g') or 0.0 for m in metrics],
        'mortality': [m['death_count'] for m in metrics],
        'cull_actual': [m.get('cull_count') or 0 for m in metrics],
        'mortality_standard': [m.get('standard_mortality') or 0.0 for m in metrics],
        'weight_gains': [m['weight_gain'] for m in metrics],
        'weight_gain_standard': [m.get('standard_weight_gain') or 0.0 for m in metrics],
        'mortality_pct': [(m['death_count'] / intake_birds * 100) if intake_birds > 0 else 0 for m in metrics]
    }

    return render_template('broiler/broiler_flock_detail.html', flock=flock, metrics=metrics, chart_data=chart_data, active_flocks=active_flocks)


from app.utils import log_user_activity, dept_required, get_dashboard_url
from flask_login import login_required, current_user


@broiler_bp.route('/flock/<int:flock_id>/delete', methods=['POST'])
@login_required
@dept_required('Breeder')
def delete_flock(flock_id):
    if not current_user.role == 'Admin':
        flash('Access Denied: Admins only.', 'danger')
        return redirect(url_for('broiler.dashboard'))

    flock = BroilerFlock.query.get_or_404(flock_id)

    # Delete all associated daily logs
    BroilerDailyLog.query.filter_by(flock_id=flock.id).delete()

    # Log user activity
    flock_name = f"{flock.farm_name} - {flock.house_name}"
    log_user_activity(current_user.id, 'Delete', 'BroilerFlock', flock.id, details={'flock_name': flock_name})

    # Delete flock
    db.session.delete(flock)
    db.session.commit()

    flash("Broiler flock deleted.", "info")
    return redirect(url_for('broiler.dashboard'))

@broiler_bp.route('/daily_log/<int:log_id>/delete', methods=['POST'])
@login_required
@dept_required('Breeder')
def delete_daily_log(log_id):
    if not current_user.role == 'Admin':
        flash('Access Denied: Admins only.', 'danger')
        return redirect(url_for('broiler.dashboard'))

    log = BroilerDailyLog.query.get_or_404(log_id)
    flock_id = log.flock_id
    date_str = log.date.strftime('%Y-%m-%d') if log.date else 'N/A'

    log_user_activity(current_user.id, 'Delete', 'BroilerDailyLog', log.id, details={'date': date_str, 'flock_id': flock_id})

    db.session.delete(log)
    db.session.commit()
    flash("Daily Log deleted.", "info")
    return redirect(url_for('broiler.flock_detail', flock_id=flock_id))


@broiler_bp.route('/flock/<int:flock_id>/daily_logs/bulk_delete', methods=['POST'])
@login_required
@dept_required('Breeder')
def bulk_delete_daily_logs(flock_id):
    if not current_user.role == 'Admin':
        flash('Access Denied: Admins only.', 'danger')
        return redirect(url_for('broiler.flock_detail', flock_id=flock_id))

    flock = BroilerFlock.query.get_or_404(flock_id)
    log_ids = request.form.getlist('log_ids')

    if not log_ids:
        flash("No daily logs selected for deletion.", "warning")
        return redirect(url_for('broiler.flock_detail', flock_id=flock_id))

    try:
        ids_to_delete = [int(lid) for lid in log_ids]
    except ValueError:
        flash("Invalid daily log IDs provided.", "danger")
        return redirect(url_for('broiler.flock_detail', flock_id=flock_id))

    logs_to_delete = BroilerDailyLog.query.filter(
        BroilerDailyLog.id.in_(ids_to_delete),
        BroilerDailyLog.flock_id == flock.id
    ).all()

    if not logs_to_delete:
        flash("No matching daily logs found to delete.", "warning")
        return redirect(url_for('broiler.flock_detail', flock_id=flock_id))

    deleted_count = len(logs_to_delete)

    # Log user activity
    log_user_activity(
        current_user.id,
        'Delete',
        'BroilerDailyLog',
        flock.id,
        details={
            'action': 'bulk_delete',
            'deleted_count': deleted_count,
            'log_ids': ids_to_delete
        }
    )

    for l in logs_to_delete:
        db.session.delete(l)
    db.session.commit()

    flash(f"Successfully deleted {deleted_count} daily logs.", "success")
    return redirect(url_for('broiler.flock_detail', flock_id=flock_id))


@broiler_bp.route('/daily_entry/<int:flock_id>', methods=['GET', 'POST'])
def daily_entry(flock_id):
    flock = BroilerFlock.query.get_or_404(flock_id)

    if request.method == 'POST':
        date_str = request.form.get('date')
        death_count = int(request.form.get('death_count', 0))
        feed_receive = request.form.get('feed_receive')
        feed_type = request.form.get('feed_type')
        feed_daily_use_kg = float(request.form.get('feed_daily_use_kg', 0.0))
        body_weight_g = float(request.form.get('body_weight_g', 0.0))
        medication_vaccine = request.form.get('medication_vaccine')
        remarks = request.form.get('remarks')

        log_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

        # Calculate day_number
        day_number = (log_date - flock.intake_date).days + 1

        log = BroilerDailyLog(
            flock_id=flock.id,
            date=log_date,
            day_number=day_number,
            death_count=death_count,
            feed_receive=feed_receive,
            feed_type=feed_type,
            feed_daily_use_kg=feed_daily_use_kg,
            body_weight_g=body_weight_g,
            medication_vaccine=medication_vaccine,
            remarks=remarks
        )
        db.session.add(log)
        db.session.commit()
        flash('Daily log added successfully.', 'success')
        return redirect(url_for('broiler.daily_entry', flock_id=flock.id))

    # Fetch calculated metrics for display
    metrics = calculate_broiler_metrics(flock.id)
    today = datetime.now().date()

    return render_template('broiler/broiler_daily_entry.html', flock=flock, metrics=metrics, today=today)


import pandas as pd
import math

def extract_metadata(row_idx, df):
    # Iterate through columns from index 1 to end to find first non-null
    for col_idx in range(1, len(df.columns)):
        val = df.iloc[row_idx, col_idx]
        if pd.notna(val) and val != '':
            return val
    return None

@broiler_bp.route('/import', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            try:
                # Read the excel file into memory, without header
                df = pd.read_excel(file, header=None)

                # Extract metadata
                farm_name = extract_metadata(1, df)
                house_name = extract_metadata(2, df)
                source = extract_metadata(3, df)
                breed = extract_metadata(4, df)

                intake_birds_raw = extract_metadata(5, df)
                try:
                    intake_birds = int(float(intake_birds_raw)) if pd.notna(intake_birds_raw) else 0
                except (ValueError, TypeError):
                    intake_birds = 0

                intake_date_raw = extract_metadata(6, df)
                intake_date = pd.to_datetime(intake_date_raw, errors='coerce').date()
                if pd.isna(intake_date):
                    intake_date = datetime.utcnow().date()

                arrival_weight_raw = extract_metadata(7, df)
                try:
                    arrival_weight_g = float(arrival_weight_raw) if pd.notna(arrival_weight_raw) else 0.0
                except (ValueError, TypeError):
                    arrival_weight_g = 0.0

                # Ensure farm and house and date have string/date representation
                farm_str = str(farm_name) if pd.notna(farm_name) else ""
                house_str = str(house_name) if pd.notna(house_name) else ""

                from app.models.models import Farm, House
                farm_str_clean = farm_str.strip() if farm_str else "Default Farm"
                house_str_clean = house_str.strip() if house_str else "Default House"

                # Defensively find or create Farm
                farm = Farm.query.filter(Farm.name.ilike(farm_str_clean)).first()
                if not farm:
                    farm = Farm(name=farm_str_clean, department='Broiler')
                    db.session.add(farm)
                    db.session.flush()

                # Defensively find or create House
                house = House.query.filter(House.name.ilike(house_str_clean), House.farm_id == farm.id).first()
                if not house:
                    house = House(name=house_str_clean, farm_id=farm.id)
                    db.session.add(house)
                    db.session.flush()

                # Find or create flock
                flock = BroilerFlock.query.filter_by(
                    farm_id=farm.id,
                    house_id=house.id,
                    intake_date=intake_date
                ).first()

                if not flock:
                    flock = BroilerFlock(
                        farm_id=farm.id,
                        house_id=house.id,
                        farm_name=farm_str_clean,
                        house_name=house_str_clean,
                        source=str(source) if pd.notna(source) else "",
                        breed=str(breed) if pd.notna(breed) else "",
                        intake_birds=intake_birds,
                        intake_date=intake_date,
                        arrival_weight_g=arrival_weight_g,
                        is_active=True
                    )
                    db.session.add(flock)
                    db.session.flush() # flush to get flock.id

                # Parse daily logs starting from row 11 (index 10 or 11?)
                # User said: "Loop through the daily logs starting from row index 11"
                # Row index 11 means the 12th row in the excel file if 0-indexed.
                rows_imported = 0
                for idx in range(11, len(df)):
                    row = df.iloc[idx]

                    date_raw = row[0]
                    if pd.isna(date_raw):
                        continue # Skip empty dates

                    log_date = pd.to_datetime(date_raw, errors='coerce').date()
                    if pd.isna(log_date):
                        continue

                    try:
                        day_number = int(float(row[1])) if pd.notna(row[1]) else (log_date - flock.intake_date).days + 1
                    except (ValueError, TypeError):
                        day_number = (log_date - flock.intake_date).days + 1

                    try:
                        death_count = int(float(row[2])) if pd.notna(row[2]) else 0
                    except (ValueError, TypeError):
                        death_count = 0

                    feed_receive = str(row[5]) if pd.notna(row[5]) else None
                    feed_type = str(row[6]) if pd.notna(row[6]) else None

                    try:
                        feed_daily_use_kg = float(row[7]) if pd.notna(row[7]) else 0.0
                    except (ValueError, TypeError):
                        feed_daily_use_kg = 0.0

                    try:
                        body_weight_g = float(row[9]) if pd.notna(row[9]) else 0.0
                    except (ValueError, TypeError):
                        body_weight_g = 0.0

                    try:
                        standard_fcr = float(row[13]) if pd.notna(row[13]) else 0.0
                    except (ValueError, TypeError):
                        standard_fcr = 0.0

                    remarks = str(row[14]) if pd.notna(row[14]) else None

                    # Check if log already exists
                    existing_log = BroilerDailyLog.query.filter_by(
                        flock_id=flock.id,
                        date=log_date
                    ).first()

                    if existing_log:
                        existing_log.day_number = day_number
                        existing_log.death_count = death_count
                        existing_log.feed_receive = feed_receive
                        existing_log.feed_type = feed_type
                        existing_log.feed_daily_use_kg = feed_daily_use_kg
                        existing_log.body_weight_g = body_weight_g
                        existing_log.standard_fcr = standard_fcr
                        existing_log.remarks = remarks
                    else:
                        new_log = BroilerDailyLog(
                            flock_id=flock.id,
                            date=log_date,
                            day_number=day_number,
                            death_count=death_count,
                            feed_receive=feed_receive,
                            feed_type=feed_type,
                            feed_daily_use_kg=feed_daily_use_kg,
                            body_weight_g=body_weight_g,
                            standard_fcr=standard_fcr,
                            remarks=remarks
                        )
                        db.session.add(new_log)

                    rows_imported += 1

                db.session.commit()
                flash(f'Successfully imported {rows_imported} daily log entries.', 'success')
                return redirect(url_for('broiler.dashboard'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error parsing Excel file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file format. Please upload an .xlsx or .xls file.', 'danger')
            return redirect(request.url)

    return render_template('broiler/broiler_import.html')
