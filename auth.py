# ------------------------------------------------------
# Note for me: Encryption is reversible. Hashing is not
# ------------------------------------------------------

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
import models
import hashlib
import secrets


password_hash = PasswordHash.recommended() # helps us use secure hashing algos like Argon2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token") # tells FastAPI to look for Bearer token in incoming HTTP request and inform swagger UI that user need to send Bearer token with username and password

'''Converts a plain text password to a salted and irreversible hash'''
def hash_password(password: str) -> str:
    return password_hash.hash(password=password)

'''Checks if plain text password entered during login matches with the salt in DB. Return True if so, False if not'''
def verify_password(plain_password: str, hashed_password: str)-> bool:
    return password_hash.verify(plain_password, hashed_password)

'''Generates a secure random token for password reset'''    
def generate_reset_token() -> str:
    token = secrets.token_urlsafe(32)
    return token

'''Hashes a password reset token'''
def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

'''Builds and signs a JWT for a user'''
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy() # clones a payload
    if expires_delta: # set expire to desired value if its provided
        expire = datetime.now(UTC) + expires_delta
    else: # set default expiration
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    to_encode.update({"exp": expire}) # add the expiration timestamp in the claim as "exp"
    # Serialize the payload into signed Base-64 encoded JWT string using app's secret kay and signing algo
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt

'''Decode and validate incoming token'''
def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(), # check if token was signed with our secret key and wasnt tampered with. 
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]}, # Incoming token should contain expiration and user id
        )
    except jwt.InvalidTokenError: # raise exception if token has been tampered with or missing desired claims
        return None
    else:
        return payload.get("sub") # return the user identifier mentioned in claim if all good
    
## Get current user using the user ID in token (if valid)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(models.User).where(models.User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

CurrentUser = Annotated[models.User, Depends(get_current_user)]

# Understanding - Parth
'''
Parth's understanding of this file (Authentication part): (polished by Google Gemini)
This file acts as our stateless authentication helper layer, serving two primary responsibilities: Password Security and JWT Token Lifecycle Management.
First, for Database Security:
We use pwdlib to handle password hashing. hash_password takes a plain text password and produces a secure, salted, irreversible hash to store in the database. verify_password checks a plain text password against that stored hash during the login request.

Second, for API Authentication:
Once a user's password is verified, create_access_token encodes a payload containing the user's ID inside the "sub" claim, sets an "exp" expiration timestamp, and signs the JWT using our server's secret key.
For subsequent protected endpoint requests, oauth2_scheme automatically intercepts the HTTP Authorization header and extracts the raw Bearer token.

Finally, verify_access_token validates the token by verifying our signature with our secret key, checking expiration, and ensuring the "sub" claim exists. If valid, it returns the user ID from "sub" so the API knows who is logged in; if invalid or tampered with, it safely returns None

'''