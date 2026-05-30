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
from app.models.models import House, Flock, DailyLog, User, Farm

class ChartDataApiTestCase(unittest.TestCase):
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

        # Setup Farm, House, Flock
        farm = Farm.query.filter_by(name='Test Farm').first()
        if not farm:
            farm = Farm(name='Test Farm')
            db.session.add(farm)
            db.session.commit()

        import uuid
        unique_suffix = uuid.uuid4().hex[:8]
        house = House(name=f'VA1_{unique_suffix}')
        db.session.add(house)
        db.session.commit()

        self.flock = Flock(
            flock_id=f'VA1_231027_Batch1_{unique_suffix}',
            farm_id=farm.id,
            house_id=house.id,
            intake_date=date(2023, 10, 27),
            intake_male=100,
            intake_female=100,
            status='Active'
        )
        db.session.add(self.flock)
        db.session.commit()

        # Create a few DailyLogs to aggregate
        log1 = DailyLog(
            flock_id=self.flock.id,
            date=date(2023, 10, 27),
            mortality_male=1,
            mortality_female=2,
            culls_male=0,
            culls_female=1,
            feed_program='Full Feed',
            water_reading_1=100,
            water_intake_calculated=500.0,
            feed_male_gp_bird=130.0,
            feed_female_gp_bird=120.0
        )
        log2 = DailyLog(
            flock_id=self.flock.id,
            date=date(2023, 10, 28),
            mortality_male=0,
            mortality_female=1,
            culls_male=1,
            culls_female=0,
            feed_program='Full Feed',
            water_reading_1=110,
            water_intake_calculated=600.0,
            feed_male_gp_bird=135.0,
            feed_female_gp_bird=125.0
        )
        db.session.add(log1)
        db.session.add(log2)
        db.session.commit()

        # Create user & login
        u = User.query.filter_by(username='admin_test').first()
        if not u:
            u = User(username='admin_test', dept='Breeder', role='Admin')
            u.set_password('pass')
            db.session.add(u)
            db.session.commit()

        self.app.post('/login', data={'username': 'admin_test', 'password': 'pass'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_daily_chart_data_api(self):
        response = self.app.get(f'/api/chart_data/{self.flock.id}?mode=daily')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['flock_id'], self.flock.flock_id)
        self.assertIn('dates', data)
        self.assertEqual(len(data['dates']), 2)
        self.assertIn('metrics', data)
        self.assertIn('mortality_f_pct', data['metrics'])

    def test_weekly_chart_data_api(self):
        response = self.app.get(f'/api/chart_data/{self.flock.id}?mode=weekly')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['flock_id'], self.flock.flock_id)
        self.assertIn('dates', data)
        self.assertIn('metrics', data)
        self.assertIn('mortality_f_pct', data['metrics'])

if __name__ == '__main__':
    unittest.main()
