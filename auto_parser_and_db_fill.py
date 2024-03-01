import asyncio
from scripts.ETL import add_top_100
from scripts.db_utils import tables_exists, create_db

loop = asyncio.get_event_loop()
tables_exists = loop.run_until_complete(tables_exists())
print(f"DATABASE EXISTS {tables_exists}")
if tables_exists is False:
    create_db()
    loop.run_until_complete(add_top_100(True))
    print("ALL DATA FOR TODAY ADDED")
else:
    loop.run_until_complete(add_top_100(False))
    print("ALL DATA FOR TODAY ADDED")
