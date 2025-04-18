from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class LicenseBase(BaseModel):
    key: str
    valid: bool = True

class LicenseCreate(LicenseBase):
    pass

class License(LicenseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class EmailTemplateBase(BaseModel):
    name: str
    content: str

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplate(EmailTemplateBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class RecipientBase(BaseModel):
    email: EmailStr

class RecipientCreate(RecipientBase):
    pass

class Recipient(RecipientBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SubjectBase(BaseModel):
    text: str

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SmtpCredentialBase(BaseModel):
    host: str
    port: int
    username: str
    password: str

class SmtpCredentialCreate(SmtpCredentialBase):
    pass

class SmtpCredential(SmtpCredentialBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
