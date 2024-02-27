import datetime

from fastapi.params import Path, Query
from starlette import status
from starlette.exceptions import HTTPException


def get_repo_activity_validation(owner: str = Path(..., description="Repository name"),
                                 repo: str = Path(..., description="Repository name"),
                                 since: datetime.date = Query("2023-08-21", convert=True),
                                 until: datetime.date = Query("2023-08-21", convert=True)):
    # todo добавить проверку есть ли owner и repo в бдшке иначе отдавать типа данных нет
    if until < since:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Неправильно выбран промежуток дат")

    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Таких владельцев и/или репозиториев нет")
    return {'owner': owner, 'repo': repo, "since": since, "until": until}
