from typing import Optional
from source.schemas.consumer import UserResponse

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

class UserSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    second_name: str = Field(min_length=3, max_length=50)
    email_add:  EmailStr
    phone_num:  str = Field()
    birth_date:  date


class UserResponse(BaseModel):
    id: int = 1
    first_name: str
    second_name: str
    email_add:  EmailStr
    phone_num:  str
    birth_date:  date
    consumer: UserResponse | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

    

