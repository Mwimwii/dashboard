from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import ForeignKey

db = SQLAlchemy()


email_site = db.Table( "email_site",
    db.Column("email_id",db.Integer, ForeignKey("email.id")),
    db.Column("site_id",db.Integer, ForeignKey("sites.id"))
)

class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String,  nullable=False)
    port = db.Column(db.String, nullable=False)
    protocol = db.Column(db.String, nullable=False)

    
class Status(db.Model):
    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    url_id = db.Column(db.Integer, db.ForeignKey("sites.id"), nullable=False)

class Email(db.Model):
    __tablename__ = "email"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    email_address = db.Column(db.String, nullable=False, unique=True)
    sites = db.relationship("Site", secondary=email_site, backref=db.backref("emails", lazy="dynamic"))