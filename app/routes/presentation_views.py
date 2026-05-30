from flask import Blueprint, render_template, abort
from flask_login import login_required
from app.models.models import Flock
from app.utils import dept_required

presentation_views_bp = Blueprint('presentation_views', __name__, url_prefix='/presentation_studio')

@presentation_views_bp.route('/')
@presentation_views_bp.route('/<int:flock_id>')
@login_required
@dept_required(['Admin', 'Breeder', 'Management'])
def presentation_studio(flock_id=None):
    from sqlalchemy.orm import joinedload
    active_flocks = Flock.query.filter_by(status='Active').options(joinedload(Flock.house)).all()

    if flock_id is None:
        if active_flocks:
            flock = active_flocks[0]
        else:
            abort(404, "No active flocks found")
    else:
        flock = Flock.query.get_or_404(flock_id)

    return render_template('presentation_studio.html', flock=flock, active_flocks=active_flocks)

