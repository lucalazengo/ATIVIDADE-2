from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None

# Properties representing User on DB
class UserInDBBase(UserBase):
    id: int

    class Config:
        from_attributes = True

# Properties to return via API
class UserResponse(UserInDBBase):
    pass
