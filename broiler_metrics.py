from datetime import datetime, date, timedelta
from app.models.models import BroilerFlock, BroilerStandard, BroilerDailyLog

def get_broiler_standards():
    standards = BroilerStandard.query.all()
    std_map = {}
    for s in standards:
        std_map[s.age_days] = s
    return std_map

def calculate_broiler_metrics(flock_id):
    """
    Core function to process a broiler flock's logs and calculate dynamic metrics.
    Merges actual daily logs with BroilerStandards.
    """
    flock = BroilerFlock.query.get(flock_id)
    if not flock:
        return []

    logs = flock.logs
    sorted_logs = sorted(logs, key=lambda x: x.date)

    std_map = get_broiler_standards()

    daily_stats = []

    # Starting values
    current_balance = flock.intake_birds or 0
    cumulative_feed_g = 0.0
    cumulative_death = 0

    for i, log in enumerate(sorted_logs):
        day_num = log.day_number

        # Balance and mortality
        current_balance -= (log.death_count + log.cull_count)
        cumulative_death += log.death_count

        mortality_pct = (log.death_count / flock.intake_birds * 100) if flock.intake_birds > 0 else 0
        cull_pct = (log.cull_count / flock.intake_birds * 100) if flock.intake_birds > 0 else 0

        cumulative_mortality_pct = (cumulative_death / flock.intake_birds * 100) if flock.intake_birds > 0 else 0

        # Feed
        cumulative_feed_g += (log.feed_daily_use_kg * 1000)

        # FCR: Feed Conversion Ratio = Total feed consumed / Total weight of live birds
        total_live_weight_g = current_balance * log.body_weight_g
        cumulative_fcr = 0.0
        if total_live_weight_g > 0:
            cumulative_fcr = cumulative_feed_g / total_live_weight_g

        # Weight gain
        prev_weight = daily_stats[i-1]['body_weight_g'] if i > 0 else flock.arrival_weight_g
        weight_gain = log.body_weight_g - prev_weight if log.body_weight_g > 0 else 0

        # Standard mapping
        std = std_map.get(day_num)

        # Determine week based on intake
        bio_days = (log.date - flock.intake_date).days
        week_num = 0 if bio_days == 0 else ((bio_days - 1) // 7) + 1 if bio_days > 0 else (bio_days // 7)

        stats = {
            'log_id': log.id,
            'date': log.date,
            'day_number': day_num,
            'week': week_num,

            # Actuals
            'death_count': log.death_count,
            'cull_count': log.cull_count,
            'mortality_pct': mortality_pct,
            'cull_pct': cull_pct,
            'cumulative_mortality_pct': cumulative_mortality_pct,
            'feed_daily_use_kg': log.feed_daily_use_kg,
            'body_weight_g': log.body_weight_g,
            'weight_gain': weight_gain,
            'cumulative_fcr': cumulative_fcr,
            'balance': current_balance,

            # Standards
            'standard_mortality_pct': getattr(std, 'daily_depletion_rate', 0.0) * 100 if std else 0.0,
            'standard_cumulative_mortality_pct': getattr(std, 'cum_depletion_rate', 0.0) * 100 if std else 0.0,

            # Placeholders from new standard
            'water_to_feed_ratio': getattr(std, 'water_to_feed_ratio', 0.0) if std else 0.0,
            'standard_bodyweight_g': getattr(std, 'live_weight', 0.0) if std else 0.0, # Kept key for charts, but mapped to new standard
            'standard_weight_gain_g': getattr(std, 'daily_gain', 0.0) if std else 0.0, # Kept key for charts, mapped to new standard
            'avg_daily_gain': getattr(std, 'avg_daily_gain', 0.0) if std else 0.0,
            'feed_consumption': getattr(std, 'feed_consumption', 0.0) if std else 0.0,
            'cum_feed_consumption': getattr(std, 'cum_feed_consumption', 0.0) if std else 0.0,
            'standard_fcr': getattr(std, 'fcr', 0.0) if std else 0.0, # Kept key for charts, mapped to new standard
            'econ_fcr': getattr(std, 'econ_fcr', 0.0) if std else 0.0,
            'pef': getattr(std, 'pef', 0.0) if std else 0.0,
        }

        daily_stats.append(stats)

    return daily_stats

def aggregate_broiler_weekly_metrics(daily_stats):
    """
    Aggregates the daily stats array into a weekly summary
    for the broiler weekly summary table.
    """
    weeks = {}
    for ms in daily_stats:
        wk = ms['week']
        if wk not in weeks:
            weeks[wk] = {
                'week': wk,
                'death_count_sum': 0,
                'feed_total_kg': 0.0,
                'days_count': 0,
                'body_weight_sum': 0.0,
                'bw_days_count': 0,
                'latest_fcr': 0.0,
                'latest_cum_mort_pct': 0.0
            }

        weeks[wk]['death_count_sum'] += ms['death_count']
        weeks[wk]['feed_total_kg'] += ms['feed_daily_use_kg']
        weeks[wk]['days_count'] += 1

        if ms['body_weight_g'] > 0:
            weeks[wk]['body_weight_sum'] += ms['body_weight_g']
            weeks[wk]['bw_days_count'] += 1

        weeks[wk]['latest_fcr'] = ms['cumulative_fcr']
        weeks[wk]['latest_cum_mort_pct'] = ms['cumulative_mortality_pct']

    result = []
    for wk in sorted(weeks.keys()):
        w_data = weeks[wk]
        avg_bw = w_data['body_weight_sum'] / w_data['bw_days_count'] if w_data['bw_days_count'] > 0 else 0

        result.append({
            'week': wk,
            'death_count': w_data['death_count_sum'],
            'mortality_pct': w_data['latest_cum_mort_pct'],
            'total_feed_kg': w_data['feed_total_kg'],
            'avg_bodyweight_g': avg_bw,
            'fcr': w_data['latest_fcr']
        })

    return result
