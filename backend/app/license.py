import uuid
from sqlalchemy.orm import Session
from . import models

def generate_license_key():
    return "LICENSE-" + str(uuid.uuid4())

def create_license(db: Session, user_id: int):
    key = generate_license_key()
    license = models.License(key=key, user_id=user_id, valid=True)
    db.add(license)
    db.commit()
    db.refresh(license)
    return license

def validate_license(db: Session, key: str):
    license = db.query(models.License).filter(models.License.key == key, models.License.valid == True).first()
    return license is not None
