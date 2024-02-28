import psycopg2


def create_db():
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="admin", host="localhost")
    try:
        conn = psycopg2.connect(dbname="test_task_27_02_db", user="postgres", password="admin",
            host="localhost")
        conn.close()
        print("Database already exists........")
    except:
        cursor = conn.cursor()
        conn.autocommit = True
        sql = '''DROP DATABASE IF EXISTS test_task_27_02_db;'''
        cursor.execute(sql)
        sql = '''CREATE DATABASE test_task_27_02_db
                WITH 
                OWNER = postgres
                ENCODING = 'UTF8'
                LC_COLLATE = 'Russian_Russia.1251'
                LC_CTYPE = 'Russian_Russia.1251'
                TABLESPACE = pg_default
                CONNECTION LIMIT = -1;'''
        cursor.execute(sql)
        conn = psycopg2.connect(dbname="test_task_27_02_db", user="postgres", password="admin",
                                host="localhost")
        sql1="""
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
        """
        cursor.execute(sql1)
        print("Database created successfully........")

        # Closing the connection

        cursor.close()
        conn.close()

# create_db()