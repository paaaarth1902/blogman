from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

# Pydantic is the foundational data validation and serialization engine behind FastAPI

# All our pydantic models will inherit from BaseModel
# Field lets us add constraints like min, max etc
# ConfigDict lets us cofigure pydantic models in a way that we can allow DB objects to be converted directly to JSON response or things like that

'''UserCreate and UserUpdate inherit this parent schema'''
class UserBase(BaseModel): 
    username: str = Field(min_length=1, max_length=20)
    email: EmailStr = Field(max_length=100)

'''While creation of User in DB, they need to pass the password as well aong with username and email'''
class UserCreate(UserBase):
    password: str = Field(min_length=8)

'''Sepeartion of concern for UserBase - We didnt keep password in UserBase itself as UserBase is inherited in UserUpdate and if we kept password d
directly in UserBase, While updating any account, they can not do so without entering password every time
'''

'''The details of any user visible to public like their username, their id, profile pic'''
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str

'''The details of User that are only visible to the user'''
class UserPrivate(UserPublic):
    email: EmailStr

'''Defines what user can update for their profile. Either username and/or email'''
class UserUpdate(UserBase):
    username: str | None = Field(min_length=1, max_length=20)
    email: EmailStr | None = Field(max_length=100)

'''Defines the required JSON structure returned to the client upon a successful login (POST /token). 
It ensures the response strictly includes the raw JWT string (access_token) and the authentication scheme 
identifier (token_type, which is always "bearer"). In FastAPI, Token is exclusively used as O/P scehma'''
class Token(BaseModel):
    access_token: str
    token_type: str
    
'''Defines what a post generally will have'''
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

class PostCreate(PostBase):
    pass

'''Builds on PostBase to define what user should see after creating post'''
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic

'''Not Inheriting from PostBase as while updating any post, user can partially update title or content too and those fields are required in PostBase'''
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)

'''Paginated Response for all posts'''
class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

'''Request body for initiating a password reset'''
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)

'''Request body for resetting a forgotten password'''
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

'''Request body for changing a user's password'''
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


'''
Summary:
"In our FastAPI application, schemas.py uses Pydantic to establish strict data contracts at the API boundary. 
Incoming request bodies are validated against schemas like UserCreate or PostCreate (which inherit from UserBase and PostBase to enforce required fields), 
triggering an automatic 422 Unprocessable Entity response if validation fails. 
For partial updates via PATCH, schemas like UserUpdate and PostUpdate inherit directly from 
BaseModel to make all fields optional. On the outgoing side, schemas act as 
security filters: UserPublic exposes safe metadata (id, username, profile picture) for public 
endpoints, while UserPrivate extends it to include sensitive fields like email for authenticated account owners. 
Finally, Token acts strictly as an output contract for returning JWT credentials."
'''