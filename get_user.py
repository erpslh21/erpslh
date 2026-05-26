from app import create_app
from app.models.models import User
app = create_app()
with app.app_context():
    users = User.query.filter_by(role='Admin').all()
    for u in users:
        print(f"username: {u.username}, role: {u.role}, dept: {u.dept}")
