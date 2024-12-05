# from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
import subprocess
import os

# from ...dependencies.session import get_session
# from ....core.models import (
#     Resource,
#     Role,
#     Permissions,
#     ProfilePermission,
#     Manager,
#     Image,
# )
# from datetime import date
# from pydantic import SecretStr


github_router = APIRouter(prefix="/github")


@github_router.get(
    "/test",
    status_code=status.HTTP_200_OK,
)
async def test():
    try:
        # Run the pwd command
        current_directory = os.getcwd()  # Get the current directory
        print(current_directory)
        return {"current_directory": current_directory}
    except subprocess.CalledProcessError as e:
        print(f"Error executing pwd: {e}")
        return {"error": "Failed to get current directory"}


@github_router.get(
    "/push",
    status_code=status.HTTP_200_OK,
)
async def push():
    result = subprocess.run(
        ["/usr/bin/git", "pull"], capture_output=True, text=True, check=True
    )
    return {"message": "Repository updated successfully", "output": result.stdout}
