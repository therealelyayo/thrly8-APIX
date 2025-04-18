from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database, auth, email_service, license
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Thrly API Sender SaaS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        # Add default admin user if not exists
        admin_email = "admin@example.com"
        admin_password = "Chi@@3454"
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin_user:
            hashed_password = auth.get_password_hash(admin_password)
            admin_user = models.User(email=admin_email, hashed_password=hashed_password)
            db.add(admin_user)
            db.commit()
            print("Default admin user created with email:", admin_email)
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/licenses", response_model=schemas.License)
def create_user_license(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_license = license.create_license(db, current_user.id)
    return new_license

@app.get("/licenses/validate/{key}")
def validate_license_key(key: str, db: Session = Depends(get_db)):
    valid = license.validate_license(db, key)
    return {"valid": valid}

@app.post("/templates", response_model=schemas.EmailTemplate)
def create_template(template: schemas.EmailTemplateCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_template = models.EmailTemplate(name=template.name, content=template.content, user_id=current_user.id)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@app.get("/templates", response_model=List[schemas.EmailTemplate])
def list_templates(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.EmailTemplate).filter(models.EmailTemplate.user_id == current_user.id).all()

@app.post("/recipients", response_model=schemas.Recipient)
def add_recipient(recipient: schemas.RecipientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_recipient = models.Recipient(email=recipient.email, user_id=current_user.id)
    db.add(new_recipient)
    db.commit()
    db.refresh(new_recipient)
    return new_recipient

@app.get("/recipients", response_model=List[schemas.Recipient])
def list_recipients(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Recipient).filter(models.Recipient.user_id == current_user.id).all()

@app.post("/subjects", response_model=schemas.Subject)
def add_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_subject = models.Subject(text=subject.text, user_id=current_user.id)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@app.get("/subjects", response_model=List[schemas.Subject])
def list_subjects(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Subject).filter(models.Subject.user_id == current_user.id).all()

@app.post("/smtp_credentials", response_model=schemas.SmtpCredential)
def add_smtp_credential(smtp_credential: schemas.SmtpCredentialCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    existing = db.query(models.SmtpCredential).filter(models.SmtpCredential.user_id == current_user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
    new_cred = models.SmtpCredential(
        host=smtp_credential.host,
        port=smtp_credential.port,
        username=smtp_credential.username,
        password=smtp_credential.password,
        user_id=current_user.id
    )
    db.add(new_cred)
    db.commit()
    db.refresh(new_cred)
    return new_cred

@app.get("/smtp_credentials", response_model=schemas.SmtpCredential)
def get_smtp_credential(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    cred = db.query(models.SmtpCredential).filter(models.SmtpCredential.user_id == current_user.id).first()
    if not cred:
        raise HTTPException(status_code=404, detail="SMTP credentials not found")
    return cred

@app.post("/send_emails")
def send_emails(
    template_id: int,
    send_method: str = "API",
    smtp_mode: str = None,
    send_speed: float = 1.0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    template = db.query(models.EmailTemplate).filter(models.EmailTemplate.id == template_id, models.EmailTemplate.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")

    recipients = db.query(models.Recipient).filter(models.Recipient.user_id == current_user.id).all()
    subjects = db.query(models.Subject).filter(models.Subject.user_id == current_user.id).all()
    if not recipients or not subjects:
        raise HTTPException(status_code=400, detail="Recipients or subjects are empty")

    smtp_credentials = None
    if send_method == "SMTP" and smtp_mode == "smtp":
        smtp_cred = db.query(models.SmtpCredential).filter(models.SmtpCredential.user_id == current_user.id).first()
        if not smtp_cred:
            raise HTTPException(status_code=400, detail="SMTP credentials not found")
        smtp_credentials = (smtp_cred.host, smtp_cred.port, smtp_cred.username, smtp_cred.password)

    emails = [r.email for r in recipients]
    subject_texts = [s.text for s in subjects]
    results = email_service.send_bulk_emails(
        emails=emails,
        subjects=subject_texts,
        email_body_template=template.content,
        send_method=send_method,
        smtp_mode=smtp_mode,
        smtp_credentials=smtp_credentials,
        from_name="Email Support",
        send_speed=send_speed
    )
    return {"results": results}
