import datetime

from fastapi.params import Path, Query
from starlette import status
from starlette.exceptions import HTTPException

from scripts.db_utils import async_session


async def get_repo_activity_validation(owner: str = Path(..., description="Repository name"),
                                       repo: str = Path(..., description="Repository name"),
                                       since: datetime.date = Query("2023-08-21", convert=True),
                                       until: datetime.date = Query("2023-08-21", convert=True)):
    # todo добавить проверку есть ли owner и repo в бдшке иначе отдавать типа данных нет
    if until < since:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Неправильно выбран промежуток дат")
    async with async_session() as session:
        try:
            res = await session.execute(f"""
            SELECT * FROM repositories r WHERE r.name = '{repo}' AND r.owner = '{owner}'
            """)
        except:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Таких владельцев и/или репозиториев нет в топ100")
    return {'owner': owner, 'repo': repo, "since": since, "until": until}


def top100_validation(order_by: str, desc: bool):
    order_by_list = ["position_cur", "stargazercount", "watchercount", "forkcount", "openissuescount"]
    if order_by.lower() not in order_by_list or desc is None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Неправильно выбрана сортировка/порядок")
    return {"order_by": order_by, "desc": "DESC" if desc else "ASC"}
