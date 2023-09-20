import base64
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

from passlib.context import CryptContext
from app.schema import RegisterSchema, LoginSchema, ForgotPasswordSchema
from app.model import Person, Users, UsersRole, Role
from app.repository import RoleRepository, UsersRepository, UsersRoleRepository, PersonRepository, JWTRepo

# Encrypt password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:

    @staticmethod
    async def register_service(register: RegisterSchema):

        # Create uuid
        _person_id = str(uuid4())
        _users_id = str(uuid4())

        # Convert birth date type from Frontend - string to date
        birth_date = datetime.strptime(register.birth, '%d-%m-%Y')

        # Open image profile default to string base64
        with open("./media/profile.png", "rb") as file:
            image_str = base64.b64encode(file.read())
        image_str = "data:image/png;base64," + image_str.decode("utf-8")

        # Mapping request date to class entity table
        _person = Person(
            id=_person_id, 
            name=register.name, 
            birth=register.birth, 
            sex=register.sex, 
            profile=image_str, 
            phone_number=register.phone_number
                         )
        _users = Users(
            id=_users_id,
            name=register.name, 
            username=register.username, 
            email=register.email, 
            password=pwd_context(register.password), 
            person_id=_person_id
            )
        
        # Everyone who registers through our registration page makes the default as a user
        _role = await RoleRepository.find_by_role_name("user")
        _users_role = UsersRole(
            users_id=_users_id,
            role_id=_role.id 
        )

        # Checking the same username
        _username = await UsersRepository.find_by_username(register.username)
        if _username:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "Bad Request",
                    "message": "Username already exists"
                }
            )
        
        # Checking the same email
        _email = await UsersRepository.find_by_email(register.email)
        if _email:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "Bad Request",
                    "message": "Email already exists"
                }
            )
        else:   # Insert to table
            await PersonRepository.create(**_person.dict())
            await UsersRepository.create(**_users.dict())
            await UsersRoleRepository.create(**_users_role.dict())

    @staticmethod
    async def login_service(login: LoginSchema):
        _username = await UsersRepository.find_by_username(login.username)
        if _username is not None:
            if not pwd_context.verify(login.password, _username.password):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "Bad Request",
                        "message": "Password is incorrect"
                    }
                )
            return JWTRepo(data={"username": _username.username}).generate_token()
        raise HTTPException(
            status_code=404,
            detail={
                "status": "Not Found",
                "message": "User not found."
            }
        )
    
    @staticmethod
    async def forgot_password_service(forgot_password: ForgotPasswordSchema):
        _email = await UsersRepository.find_by_email(forgot_password.email)
        if _email is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "Not Found",
                    "message": "User not found."
                }
            )
        await UsersRepository.update_password(
            email=forgot_password.email,
            password=pwd_context(forgot_password.new_password)
            )

#generate roles manually
async def generate_role():
    _role = await RoleRepository.find_by_list_role_name(["admin", "user"])
    if not _role:
        roles_to_create = [
            Role(id=str(uuid4()), role_name="admin"),
            Role(id=str(uuid4()), role_name="user")
        ]
        await RoleRepository.create_list(roles_to_create)
