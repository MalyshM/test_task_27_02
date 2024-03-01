from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from scripts.ETL import get_repo_activity_
from scripts.db_utils import get_session
from validators.Repo_validators import get_repo_activity_validation, top100_validation

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
async def top100(params: Annotated[dict, Depends(top100_validation)], db: AsyncSession = Depends(get_session)):
    # C ДАТОЙ БЫЛО БЫ ПРОЩЕ
    res = await db.execute(f"""
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
                sub_query.{params['order_by']} {params['desc']}
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
async def get_repo_activity(params: Annotated[dict, Depends(get_repo_activity_validation)],
                            db: AsyncSession = Depends(get_session)):
    # БЕЗ ПОЛЕЙ АВТОРА И РЕПЫ НЕ ПОНЯТЬ, ЧТО В БД ЕСТЬ НУЖНЫЕ ДАННЫЕ
    res = await get_repo_activity_(params)
    return res
