from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from validators.Repo_validators import get_repo_activity_validation

router = APIRouter()

# todo добавить описание ответа
@router.get("/api/repos/top100", name="Repo:top100", status_code=status.HTTP_200_OK,
            tags=["Repo"], description=
            """
                    Returns:\n
                        List[]: массив на топ100 репозиториев 
            """)
async def top100():
    return "top100 will be here soon"

# todo добавить описание ответа
@router.get("/api/repos/{owner}/{repo}/activity", name='Repo:top100', status_code=status.HTTP_200_OK,
            tags=["Repo"], description=
            """
            Получает владельца репозитория и сам репозиторий
            Args: 
                owner (str): владелец.
                repo  (str): репозиторий.
            Raises:
                
            Returns:
                List[] - массив словарей с полями date, commits,
            """)
async def get_repo_activity(params: Annotated[dict, Depends(get_repo_activity_validation)]):
    # Your code here
    return {"message": f"Fetching activity for /api/repos/{params['owner']}/{params['repo']}/activity"}
