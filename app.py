from flask import render_template,  request, jsonify, redirect, g, url_for
from models import *
from ping_site import get_timestamp, utc_to_local
from flask import Flask
import requests
from os.path import abspath, join
from os import environ, path
from dotenv import load_dotenv
from decouple import config

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

# Flask Configurations
app = Flask(__name__)
app.config["SECRET_KEY"] = config("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config("SQLALCHEMY_TRACK_MODIFICATIONS", cast = bool)

db.init_app(app)


# Helper functions
def add_new_site(name, url, port,protocol, count_sites):
    new_site = Site(name=name, url=url, port=port, protocol=protocol)
    init_status = Status(timestamp=get_timestamp(), status="INITIALIZING", url_id=count_sites+1)
    db.session.add(new_site)
    db.session.add(init_status)
    db.session.commit()

def check_site_valid(site, protocol):
    try:
        response = requests.get(f"{protocol}://{site}")
    except Exception as err:
        print(err)
        response = None
    return response

# Routes/Views
@app.route('/', methods=["GET", "POST"])
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

ROWS_PER_PAGE = 15
# Route for the IP details page
@app.route('/ip/<int:url_id>')
def ip(url_id):
    page = request.args.get('page', type=int)
    status = Status.query.order_by(Status.timestamp.desc()).filter_by(url_id=url_id).paginate(page=page, per_page=ROWS_PER_PAGE)
    site = Site.query.get(url_id)
    site_page = status
    status = list({"timestamp":f"{utc_to_local(s.timestamp):%B %d, %Y - %H:%M:%S%z}", "status":s.status} for s in status.items)
    return render_template("site_details.html", site_page=site_page, status=status, site=site)

@app.route('/ip/<int:url_id>/remove')
def remove(url_id, err=0):
    site = Site.query.get(url_id)
    db.session.delete(site)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/ip/<int:url_id>/edit', methods=["GET", "POST"] )
def edit(url_id):
    site = Site.query.get(url_id)
    print(site.protocol)
    if request.method == "POST":
        site.name = request.form.get("name")
        site.url = request.form.get("url")
        site.port = request.form.get("port")
        site.protocol = request.form.get("protocol")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit_site_form.html",site=site )

# test route
@app.route('/ip/<url_id>/email/add', methods=["GET", "POST"] )
def add_email(url_id):
    print(url_id)
    # Send the site_id    
    if request.method == "POST":
        email_address = request.form.get("email")
        name = request.form.get("name")
        site = Site.query.get(url_id)
        email = Email.query.filter_by(email_address=email_address).first()
        # print(email)
        if email is None:
            email = Email(name =name,email_address = email_address)
            db.session.add(email)
        # Creates an entry in the association table
        site.emails.append(email)
        db.session.commit()
        return redirect(url_for('ip', url_id=url_id))
    return render_template("add_email.html", url_id=url_id)

@app.route('/ip/<url_id>/email/remove/<email_id>', methods=["GET", "POST"] )
def remove_email(url_id, email_id):
    site = Site.query.get(url_id)
    email = Email.query.get(email_id)
    site.emails.remove(email)
    db.session.commit()
    return redirect(url_for('ip', url_id=url_id))

@app.route('/ip/<int:url_id>/email/edit', methods=["GET", "POST"] )
def edit_email(url_id):
    site = Site.query.get(url_id)
    print(site.protocol)
    if request.method == "POST":
        site.name = request.form.get("name")
        site.url = request.form.get("url")
        site.port = request.form.get("port")
        site.protocol = request.form.get("protocol")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit_site_form.html",site=site )



@app.route('/form')
def form():
    return render_template("add_site_form.html")

# API
# Routes/Views
@app.route('/api/all')
def apihome():
    """ The home route that displays all the available sites.
        The database is first queried on the sites table and 
        then joined with the status of the sites as a result.

        Using a POST method proceeds to add a new site 
    """
    sites  = Site.query.all()
    status = []
    for site in sites:
        status.append(Status.query.filter_by(url_id=site.id).order_by(Status.id.desc()).first())
    sites = list(dict(name=site.name, url=site.url, timestamp=stat.timestamp, status=stat.status, url_id=stat.url_id) for site, stat in zip(sites, status))
    return jsonify(sites)

@app.route("/api/<int:url_id>")
def api(url_id):
    # 
    status = Status.query.order_by(Status.timestamp.desc()).filter_by(url_id=url_id)
    status = list({"timestamp":s.timestamp, "status":s.status} for s in status)
    for sta in status:
        if sta["status"] == "ON":
            sta["status_val"] = 1
        else:
            sta["status_val"] = 0
    return jsonify(status)

@app.route("/apibetween/<int:url_id>")
def api_between(url_id):
    # 
    status = Status.query.filter(Status.timestamp.between("2021-01-20 12:00:00","2021-01-20 13:00:00")).order_by(Status.timestamp.desc()).filter_by(url_id=url_id).paginate(page=1, per_page=3)
    status = list({"timestamp":s.timestamp, "status":s.status} for s in status.items)
    for sta in status:
        if sta["status"] == "ON":
            sta["status_val"] = 1
        else:
            sta["status_val"] = 0
    return jsonify(status)

@app.route("/test/<int:url_id>")
def test():
    return