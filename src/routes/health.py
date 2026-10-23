from fastapi import APIRouter, HTTPException, Request

router = APIRouter(
    prefix="/health/v1",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

@router.get("/check")
async def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: A dictionary containing the status of the API.
    """
    try:
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database")
async def database_health_check(request: Request):
    """
    Database health check endpoint to verify the database is running.

    Returns:
        dict: A dictionary containing the status of the database.
    """
    try:
        # Perform a simple query to check database connectivity
        # This is a placeholder - replace with actual database check logic
        client = request.app.state.mongo_client
        await client.admin.command("ping")
        return {"status": "database healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))