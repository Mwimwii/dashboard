from sqlalchemy.orm import Session
import models
import schemas

def get_site(db: Session, site_id: int):
    pass

def get_admin(db: Session, admin_id: int):
    pass

def get_websites(db: Session, skip: int = 0, limit: int = 100):
    pass

def create_admin(db: Session, admin: schemas.WebAdmin):
    pass

def get_admins(db: Session, skip: int = 0, limit: int = 100):
    pass

