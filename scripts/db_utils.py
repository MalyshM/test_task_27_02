import os

import psycopg2
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Repository, RepoActivity


def create_db():
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="admin", host="localhost")
    cursor = conn.cursor()
    conn.autocommit = True
    sql = '''DROP DATABASE IF EXISTS test_task_27_02_db;'''
    cursor.execute(sql)
    sql = '''CREATE DATABASE test_task_27_02_db
            WITH 
            OWNER = postgres
            ENCODING = 'UTF8'
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1;'''
    cursor.execute(sql)
    conn = psycopg2.connect(dbname="test_task_27_02_db", user="postgres", password="admin",
                            host="localhost")
    cursor = conn.cursor()
    conn.autocommit = True
    sql1 = '''
    DROP TABLE IF EXISTS repositories CASCADE;
DROP TABLE IF EXISTS repo_activity CASCADE;

CREATE TABLE repositories (
    id              BIGSERIAL   PRIMARY KEY,
    name            VARCHAR     NOT NULL,
    owner           VARCHAR     NOT NULL,
    position_cur    INTEGER     NOT NULL,
    position_prev   INTEGER,
    stargazerCount  INTEGER     NOT NULL,
    watcherCount    INTEGER     NOT NULL,
    forkCount       INTEGER     NOT NULL,
    openIssuesCount INTEGER     NOT NULL,
    primaryLanguage VARCHAR
);

CREATE TABLE repo_activity (
    id      BIGSERIAL PRIMARY KEY,
    date    TIMESTAMP,
    commits INT,
    authors VARCHAR[]
);
        '''
    cursor.execute(sql1)
    print("Database created successfully........")
    cursor.close()
    conn.close()


async def tables_exists():
    try:

        async with async_session() as session:
            res = await session.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'repositories'
        ) AS repositories_exists,
        EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'repo_activity'
        ) AS repo_activity_exists;""")
            res_true = res.scalars().first()
            return res_true
    except:
        return False


def add_data():
    conn = psycopg2.connect(dbname="test_task_27_02_db", user="postgres", password="admin",
                            host="localhost")
    cur = conn.cursor()
    with open('data/top_100_current.csv', 'r', encoding='utf-8') as csv_file:
        cur.copy_from(csv_file, 'repositories', sep='[', null='NULL')
    cur.close()
    conn.commit()
    conn.close()


async def add_data_async(data: dict):
    async with async_session() as session:
        repo = session.add(Repository(id=data["id"], name=data["name"], owner=data["owner"],
                                      position_cur=data["position_cur"], position_prev=data["position_prev"],
                                      stargazercount=data["stargazerCount"],
                                      watchercount=data["watcherCount"], forkcount=data["forkCount"],
                                      openissuescount=data["openIssuesCount"], primarylanguage=data["primaryLanguage"]))
        await session.commit()
    return 0


async def add_data_async_repo_activity(data: dict):
    async with async_session() as session:
        repo = session.add(RepoActivity(date=data["date"], commits=data["commits"], authors=data["authors"]))
        await session.commit()
    return {"date": data["date"], "commits": data["commits"], "authors": data["authors"]}


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(tables_exists())
