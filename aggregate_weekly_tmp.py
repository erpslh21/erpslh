def aggregate_broiler_weekly(daily_stats, intake_birds, arrival_weight_g):
    """
    Aggregates daily broiler stats into weekly summary and a cumulative summary.
    """
    import math

    weeks_data = {}
    for m in daily_stats:
        week = math.ceil(m['day_number'] / 7)
        if week not in weeks_data:
            # Determine start balance and start weight for the week
            # If it's the first day of the week, the start balance is the previous day's balance
            # For week 1, day 1, it's intake_birds.
            weeks_data[week] = {
                'week': week,
                'death_count': 0,
                'total_feed_kg': 0.0,
                'total_feed_g_per_bird': 0.0, # for weekly FCR
                'bws': [],
                'daily_bws': {}, # maps day_number to body_weight
            }

            # Find the starting values for this week
            start_day = (week - 1) * 7 + 1
            # We need the balance right before this week started.
            # If week 1, it's intake_birds.
            # If week 2, it's the balance at the end of day 7.
            if week == 1:
                weeks_data[week]['start_balance'] = intake_birds
                weeks_data[week]['start_weight_g'] = arrival_weight_g
            else:
                # Find the log for day (start_day - 1)
                prev_day_stat = next((s for s in daily_stats if s['day_number'] == start_day - 1), None)
                if prev_day_stat:
                    weeks_data[week]['start_balance'] = prev_day_stat['balance']
                    weeks_data[week]['start_weight_g'] = prev_day_stat['body_weight_g']
                else:
                    # Fallback if logs are missing (should not happen ideally)
                    weeks_data[week]['start_balance'] = intake_birds
                    weeks_data[week]['start_weight_g'] = arrival_weight_g

        weeks_data[week]['death_count'] += m['death_count']
        weeks_data[week]['total_feed_kg'] += m['feed_daily_use_kg']
        weeks_data[week]['total_feed_g_per_bird'] += m['gram_per_bird']
        weeks_data[week]['bws'].append(m['body_weight_g'])
        weeks_data[week]['daily_bws'][m['day_number']] = m['body_weight_g']
        weeks_data[week]['end_balance'] = m['balance'] # constantly update to get the final one

    weekly_summary = []

    total_cum_feed_kg = 0.0
    total_cum_death = 0
    latest_avg_bw = 0.0
    latest_cum_fcr = 0.0

    for w in sorted(weeks_data.keys()):
        d = weeks_data[w]

        # Weekly Mortality % = (deaths in week / start balance of week) * 100
        start_bal = d['start_balance']
        mortality_pct = (d['death_count'] / start_bal * 100) if start_bal and start_bal > 0 else 0.0

        # Weekly Avg BW: simple average of BW inputs for that week
        # (Though usually it's just the final BW of the week, user specifically asked to keep existing avg logic "simple average of BW inputs")
        avg_bw = sum(d['bws']) / len(d['bws']) if d['bws'] else 0.0

        # Weekly FCR: feed consumed ONLY in that week / weight gained ONLY in that week
        # Feed consumed in week per bird = d['total_feed_g_per_bird']
        # Weight gained in week = (latest BW in week) - (start weight of week)
        latest_bw_in_week = d['bws'][-1] if d['bws'] else 0.0
        weight_gain_in_week = latest_bw_in_week - d['start_weight_g']

        weekly_fcr = d['total_feed_g_per_bird'] / weight_gain_in_week if weight_gain_in_week > 0 else 0.0

        weekly_summary.append({
            'week': d['week'],
            'death_count': d['death_count'],
            'mortality_pct': mortality_pct,
            'total_feed_kg': d['total_feed_kg'],
            'avg_bodyweight_g': avg_bw,
            'fcr': weekly_fcr
        })

        # Update cumulatives
        total_cum_death += d['death_count']
        total_cum_feed_kg += d['total_feed_kg']

    if daily_stats:
        last_stat = daily_stats[-1]
        latest_avg_bw = last_stat['body_weight_g'] # Or keep the simple average over the last week? Prompt didn't complain about cumulative avg bw. Let's look at the api.py for cumulative.
        latest_cum_fcr = last_stat['cumulative_fcr']

    return weekly_summary, None
