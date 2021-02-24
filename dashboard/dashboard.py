import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import * 
from ping_site import utc_to_local

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
def index():
    """ The home route that displays all the available sites.
        The database is first queried on the sites table and 
        then joined with the status of the sites as a result.

        Using a POST method proceeds to add a new site 
    """

    sites  = Site.query.all()

    if request.method == "POST":
        name = (request.form.get("name"))
        url = (request.form.get("url"))
        port = (request.form.get("port"))
        protocol = (request.form.get("protocol"))
        # redirect(url_for("form", protocol=protocol))
        add_new_site(name, url, port, protocol,len(sites))
        
    status = []
    for site in sites:
        status.append(Status.query.filter_by(url_id=site.id).order_by(Status.id.desc()).first())
    sites = list(dict(name=site.name, url=site.url,timestamp= utc_to_local(stat.timestamp), status=stat.status, url_id=stat.url_id, port=site.port) for site, stat in zip(sites, status))
    return render_template("home.html", sites=sites)
