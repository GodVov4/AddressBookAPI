from datetime import date
from pydantic import BaseModel, EmailStr, Field, PastDate


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    surname: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(min_length=6, max_length=50)
    number: str = Field(min_length=9, max_length=20)
    birthday: date = Field(PastDate())
    description: str = Field(min_length=3, max_length=250)


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: str
    number: str
    birthday: str
    description: str

    class Config:
        from_attributes = True
