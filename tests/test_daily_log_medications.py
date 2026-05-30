import unittest
import sys
import os
import importlib.util
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('main_app', os.path.join(os.path.dirname(__file__), '..', 'run.py'))
main_app = importlib.util.module_from_spec(spec)
sys.modules['main_app'] = main_app
spec.loader.exec_module(main_app)

app = main_app.create_app()
from app.database import db
from app.models.models import House, Flock, Medication, User, Farm, DailyLog, InventoryItem, InventoryTransaction

class DailyLogMedicationsTestCase(unittest.TestCase):
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

        # Create Breeder Farm
        self.farm = Farm(name='Breeder Farm A', department='Breeder')
        db.session.add(self.farm)
        db.session.commit()

        # Create House
        self.house = House(name='VA1', farm_id=self.farm.id)
        db.session.add(self.house)
        db.session.commit()

        # Create Flock
        self.flock = Flock(
            flock_id='VA1-TEST',
            farm_id=self.farm.id,
            house_id=self.house.id,
            intake_date=date(2023, 1, 1),
            intake_male=100,
            intake_female=100
        )
        db.session.add(self.flock)
        db.session.commit()

        # Create Medication Inventory Item
        self.inv_item = InventoryItem(
            name='Aspirin',
            type='Medication',
            unit='Kg',
            current_stock=10.0,
            location='Breeder'
        )
        db.session.add(self.inv_item)
        db.session.commit()

        # Create User assigned to Breeder Farm A
        self.user = User(username='breeder_user', dept='Breeder', role='Supervisor', farm_id=self.farm.id)
        self.user.set_password('pass')
        db.session.add(self.user)
        db.session.commit()

        self.app.post('/login', data={'username': 'breeder_user', 'password': 'pass'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_submit_daily_log_with_medications(self):
        # Submit daily log for 2023-01-01
        response = self.app.post('/daily_log', data={
            'house_id': self.house.id,
            'date': '2023-01-01',
            'eggs_collected': 50,
            'egg_weight': 55.0,
            'cull_eggs_jumbo': 1,
            'cull_eggs_small': 2,
            'cull_eggs_abnormal': 0,
            'cull_eggs_crack': 1,
            'feed_program': 'Full Feed',
            'feed_male_gp_bird': '130.0',
            'feed_female_gp_bird': '110.0',
            # Inline Medications parameters
            'med_inventory_id[]': [str(self.inv_item.id)],
            'med_drug_name[]': ['Aspirin'],
            'med_dosage[]': ['1g/L'],
            'med_amount_qty[]': ['2.5'],
            'med_amount_used[]': ['2.5'],
            'med_remarks[]': ['Test Remark']
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify DailyLog was created/updated
        log = DailyLog.query.filter_by(flock_id=self.flock.id, date=date(2023, 1, 1)).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.eggs_collected, 50)
        self.assertEqual(log.cull_eggs_jumbo, 1)

        # Verify Medication record was created
        med = Medication.query.filter_by(flock_id=self.flock.id, start_date=date(2023, 1, 1)).first()
        self.assertIsNotNone(med)
        self.assertEqual(med.drug_name, 'Aspirin')
        self.assertEqual(med.dosage, '1g/L')
        self.assertEqual(med.amount_used_qty, 2.5)
        # End date must default strictly to s_date (2023-01-01)
        self.assertEqual(med.end_date, date(2023, 1, 1))

        # Verify Inventory Item deduction
        updated_item = InventoryItem.query.get(self.inv_item.id)
        self.assertEqual(updated_item.current_stock, 7.5)

        # Verify InventoryTransaction creation
        tx = InventoryTransaction.query.filter_by(inventory_item_id=self.inv_item.id, transaction_type='Usage').first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.quantity, 2.5)
        self.assertEqual(tx.transaction_date, date(2023, 1, 1))

    def test_edit_daily_log_reverts_and_updates_medications(self):
        # Initial submission
        self.app.post('/daily_log', data={
            'house_id': self.house.id,
            'date': '2023-01-01',
            'eggs_collected': 50,
            'med_inventory_id[]': [str(self.inv_item.id)],
            'med_drug_name[]': ['Aspirin'],
            'med_dosage[]': ['1g/L'],
            'med_amount_qty[]': ['2.0'],
            'med_amount_used[]': ['2.0']
        })

        # Verify stock was deducted to 8.0
        self.assertEqual(InventoryItem.query.get(self.inv_item.id).current_stock, 8.0)

        # Edit/resubmit the log with updated medication amount and remarks
        response = self.app.post('/daily_log', data={
            'house_id': self.house.id,
            'date': '2023-01-01',
            'eggs_collected': 60,
            'med_inventory_id[]': [str(self.inv_item.id)],
            'med_drug_name[]': ['Aspirin'],
            'med_dosage[]': ['2g/L'],
            'med_amount_qty[]': ['3.5'],
            'med_amount_used[]': ['3.5'],
            'med_remarks[]': ['Updated remark']
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify there is exactly 1 Medication record (preventing duplicates)
        meds = Medication.query.filter_by(flock_id=self.flock.id, start_date=date(2023, 1, 1)).all()
        self.assertEqual(len(meds), 1)
        self.assertEqual(meds[0].dosage, '2g/L')
        self.assertEqual(meds[0].amount_used_qty, 3.5)

        # Verify stock was correctly reverted and re-deducted: 10.0 - 3.5 = 6.5
        self.assertEqual(InventoryItem.query.get(self.inv_item.id).current_stock, 6.5)

        # Verify there is only one usage transaction
        txs = InventoryTransaction.query.filter_by(inventory_item_id=self.inv_item.id, transaction_type='Usage').all()
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].quantity, 3.5)

if __name__ == '__main__':
    unittest.main()
