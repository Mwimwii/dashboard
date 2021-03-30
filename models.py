from datetime import date
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.schema import ForeignKey, Table
from sqlalchemy.types import DateTime
from database import Base # if Unix devices raise error use .database...


admin_sites_table = Table(
    'adminsites',
     Base.metadata,
     Column('admin_id', Integer, ForeignKey('admins.id')),
     Column('site_id', Integer, ForeignKey('sites.id'))
)


class Website(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False)
    port = Column(String, nullable=False)
    protocol = Column(String, nullable=False)

class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    url_id = Column(Integer, ForeignKey('sites.id'), nullable=False)

class WebAdmins(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    email_address = Column(String, nullable=false, unique=True)
    sites = relationship(
        'Website',
        secondary=admin_sites_table,
        backref=backref('admins', lazy='dynamic')
    )