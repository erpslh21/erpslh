import re

with open('app/models/models.py', 'r') as f:
    content = f.read()

bodyweight_models = """
class FlockBodyweight(VersionedMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flock_id = db.Column(db.Integer, db.ForeignKey('flock.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    age_week = db.Column(db.Integer, nullable=True) # Explicitly track the week

    body_weight_male = db.Column(db.Float, default=0.0)
    body_weight_female = db.Column(db.Float, default=0.0)
    uniformity_male = db.Column(db.Float, default=0.0)
    uniformity_female = db.Column(db.Float, default=0.0)

    standard_bw_male = db.Column(db.Integer, nullable=True)
    standard_bw_female = db.Column(db.Integer, nullable=True)

    flock = db.relationship('Flock', backref=db.backref('bodyweights', cascade="all, delete-orphan"))

class FlockBodyweightPartition(VersionedMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bodyweight_id = db.Column(db.Integer, db.ForeignKey('flock_bodyweight.id'), nullable=False, index=True)
    partition_name = db.Column(db.String(10), nullable=False) # F1, F2, F3, F4, M1, M2
    body_weight = db.Column(db.Float, default=0.0)
    uniformity = db.Column(db.Float, default=0.0)

    bodyweight = db.relationship('FlockBodyweight', backref=db.backref('partitions', cascade="all, delete-orphan"))
"""

if "class FlockBodyweightPartition" not in content:
    # Insert right before PartitionWeight
    content = content.replace("class PartitionWeight", bodyweight_models + "\nclass PartitionWeight")
    with open('app/models/models.py', 'w') as f:
        f.write(content)
    print("Added bodyweight models.")
else:
    print("Models already exist.")
