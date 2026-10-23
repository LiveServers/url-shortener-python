from typing import List

from fastapi import APIRouter, HTTPException
from src.models.user import User


router = APIRouter(
    prefix="/users/v1",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", response_model=User)
async def create_user(user: User):
    """
    Create a new user.

    Args:
        user (User): The user data to create.

    Returns:
        User: The created user.
    """
    try:
        existing_user = await User.find_one(User.email == user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        await user.insert()

        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#TO-DO: remove this later, just for testing purposes
@router.get("/retrieve-users", response_model=List[User])
async def get_users():
    """
    Retrieve all users.

    Returns:
        List[User]: A list of all users.
    """
    try:
        users = await User.find_all().to_list()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
