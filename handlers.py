from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from scripts.db_utils import get_session
from validators.Repo_validators import get_repo_activity_validation

router = APIRouter()


@router.get("/api/repos/top100", name="Repo:top100", status_code=status.HTTP_200_OK,
            tags=["Repo"], description=
            """
                    Returns:
                        List[]: массив на топ100 репозиториев\n
                    
                [
                  {
                    "name": "freeCodeCamp", название репозитория
                    "owner": "freeCodeCamp", хозяин репозитория
                    "position_cur": 1, текущая позиция
                    "position_prev": 1, вчерашняя позиция
                    "stargazercount": 384284, количество звездочек
                    "watchercount": 8497, количество смотрящих на момент парсинга
                    "forkcount": 34753, количество веток
                    "openissuescount": 268, количество ОТКРЫТЫХ проблем
                    "primarylanguage": "TypeScript" Основной язык
                  },
            """)
async def top100(db: AsyncSession = Depends(get_session)):
    res = await db.execute("""
        SELECT *
            FROM (
                SELECT
                    r.name,
                    r.owner,
                    r.position_cur,
                    r.position_prev,
                    r.stargazerCount,
                    r.watcherCount,
                    r.forkCount,
                    r.openIssuesCount,
                    r.primaryLanguage
                FROM
                    repositories r
                ORDER BY
                    r.id DESC
                LIMIT 100
            ) AS sub_query
            ORDER BY
                sub_query.position_cur ASC
    """)
    return res.fetchall()


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
