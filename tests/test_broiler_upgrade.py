import unittest
import sys
import os
import importlib.util
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('main_app', os.path.join(os.path.dirname(__file__), '..', 'run.py'))
main_app = importlib.util.module_from_spec(spec)
sys.modules['main_app'] = main_app
spec.loader.exec_module(main_app)

app = main_app.create_app()
from app.database import db
from app.models.models import House, Farm, BroilerFlock, BroilerDailyLog, User, BroilerStandard

class BroilerUpgradeTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['RATELIMIT_ENABLED'] = False
        from app.extensions import limiter
        limiter.enabled = False

        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

        db.create_all()

        # Set up standard Broiler Farm and Houses
        self.farm = Farm(name='Broiler Farm A', department='Broiler')
        db.session.add(self.farm)
        db.session.commit()

        self.house1 = House(name='House 1', farm_id=self.farm.id)
        self.house2 = House(name='House 2', farm_id=self.farm.id)
        db.session.add(self.house1)
        db.session.add(self.house2)
        db.session.commit()

        # Create active BroilerFlock 1
        self.flock1 = BroilerFlock(
            farm_id=self.farm.id,
            house_id=self.house1.id,
            farm_name=self.farm.name,
            house_name=self.house1.name,
            breed='Cobb 500',
            intake_birds=10000,
            intake_date=date(2026, 5, 10),
            arrival_weight_g=42.0,
            is_active=True
        )
        # Create active BroilerFlock 2
        self.flock2 = BroilerFlock(
            farm_id=self.farm.id,
            house_id=self.house2.id,
            farm_name=self.farm.name,
            house_name=self.house2.name,
            breed='Cobb 500',
            intake_birds=12000,
            intake_date=date(2026, 5, 12),
            arrival_weight_g=41.5,
            is_active=True
        )
        db.session.add(self.flock1)
        db.session.add(self.flock2)
        db.session.commit()

        # Add daily logs to self.flock1
        log1 = BroilerDailyLog(
            flock_id=self.flock1.id,
            date=date(2026, 5, 10),
            day_number=1,
            death_count=10,
            cull_count=5,
            feed_daily_use_kg=120.0,
            body_weight_g=55.0
        )
        log2 = BroilerDailyLog(
            flock_id=self.flock1.id,
            date=date(2026, 5, 11),
            day_number=2,
            death_count=12,
            cull_count=8,
            feed_daily_use_kg=130.0,
            body_weight_g=68.0
        )
        db.session.add(log1)
        db.session.add(log2)

        # Add Broiler Standards
        std1 = BroilerStandard(age_days=1, live_weight=52.0, fcr=0.08, cum_depletion_rate=0.1)
        std2 = BroilerStandard(age_days=2, live_weight=65.0, fcr=0.12, cum_depletion_rate=0.2)
        db.session.add(std1)
        db.session.add(std2)
        db.session.commit()

        # Create user & login
        u = User.query.filter_by(username='admin_test').first()
        if not u:
            u = User(username='admin_test', dept='Broiler', role='Admin')
            u.set_password('pass')
            db.session.add(u)
            db.session.commit()

        self.app.post('/login', data={'username': 'admin_test', 'password': 'pass'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_broiler_dashboard_data(self):
        response = self.app.get('/broiler/dashboard')
        self.assertEqual(response.status_code, 200)
        # Check active and harvested contexts are passed
        self.assertIn(b'Broiler Farm A', response.data)
        self.assertIn(b'House 1', response.data)

    def test_compare_metrics_api(self):
        # Test Bodyweight comparison
        response = self.app.get(f'/api/broiler/compare_metrics?farm_id={self.farm.id}&metric=body_weight_g')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('days', data)
        self.assertIn('standards', data)
        self.assertIn('series', data)
        self.assertIn('House 1', data['series'])
        self.assertEqual(data['series']['House 1'][0], 55.0) # Day 1 body weight

        # Test FCR comparison
        response = self.app.get(f'/api/broiler/compare_metrics?farm_id={self.farm.id}&metric=fcr')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('House 1', data['series'])

    def test_harvest_flock_action(self):
        # Harvest flock 1
        payload = {
            'harvest_date': '2026-06-15',
            'harvested_birds': 9800,
            'harvest_fcr': 1.62,
            'harvest_avg_weight': 1850.0
        }
        response = self.app.post(f'/broiler/flock/{self.flock1.id}/harvest', data=payload)
        self.assertEqual(response.status_code, 302) # Redirect to dashboard

        # Verify flock is now harvested (is_active = False)
        updated_flock = BroilerFlock.query.get(self.flock1.id)
        self.assertFalse(updated_flock.is_active)
        self.assertEqual(updated_flock.harvested_birds, 9800)
        self.assertEqual(updated_flock.harvest_fcr, 1.62)
        self.assertEqual(updated_flock.harvest_avg_weight, 1850.0)

if __name__ == '__main__':
    unittest.main()
