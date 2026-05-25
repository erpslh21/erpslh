import re
with open('app/services/data_service.py', 'r') as f:
    content = f.read()

# I want to add FlockBodyweight logic in `generate_spreadsheet_data`
if "FlockBodyweight" not in content:
    content = content.replace("from app.models.models import Flock, DailyLog", "from app.models.models import Flock, DailyLog, FlockBodyweight")
    with open('app/services/data_service.py', 'w') as f:
        f.write(content)
