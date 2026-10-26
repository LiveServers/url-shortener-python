from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException
from src.models.user import User
from src.models.api_key import APIKey
from src.utils.api_key import generate_api_key

router = APIRouter(
    prefix="/api_keys/v1",
    tags=["api_keys"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", response_model=APIKey)
async def create_api_key(userid: PydanticObjectId):
    """
    Create a new API key for a user.

    Args:
        userid (PydanticObjectId): The ID of the user for whom the API key is being created.
        """
    try:
        existing_user = await User.find_one(User.id == userid)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        api_key_response = generate_api_key()

        credential = APIKey(
            api_key=api_key_response["api_key"],
            user_id=userid,
            expires_at=api_key_response["expires_at"],
            encrypted_secret=api_key_response["encrypted_secret"],
        )

        await credential.insert()
        return credential
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))