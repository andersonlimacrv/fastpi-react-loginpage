from fastapi import HTTPException
import logging
import re
from typing import TypeVar, Optional

from pydantic import BaseModel, validator
from sqlalchemy import false
from app.model.person import Sex


T = TypeVar('T')

# get root logger
logger = logging.getLogger(__name__)

class RegisterSchema(BaseModel):

    username: str
    email: str
    password: str
    phone_number: str
    sex: Sex
    profile: str = "base64"


    #phone number validation
    @validator('phone_number')
    def phone_number_validation(cls, phone_number):
        logger.debug(f"phone_number: {phone_number}")

        #regex phone number pt_br
        phone_br_pattern = r'^\+?55[1-9][0-9]{1,14}$'
        if phone_number and not re.search(phone_br_pattern, phone_number, re.I):
            raise HTTPException(status_code=400, detail={'status': 'Bad Request', 'message': 'Invalid input phone number'})
        return phone_number
    #Sex validation
    @validator('sex')
    def sex_validation(cls, sex):
        if hasattr(Sex, sex) is False:
            raise HTTPException(status_code=400, detail={'status': 'Bad Request', 'message': 'Invalid input sex'})
        return sex
   
class LoginSchema(BaseModel):
    username: str
    password: str

class ForgotPasswordSchema(BaseModel):
    email: str
    new_password: str

class DetailSchema(BaseModel):
    status: str
    message: str
    result : Optional[T] = None

class ResponseSchema(BaseModel):
    detail: str
    result : Optional[T] = None

    

