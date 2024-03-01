import asyncio
import json
from datetime import datetime

import aiohttp
import requests
import pandas as pd
import sqlalchemy as sqlalchemy
from dotenv import load_dotenv
import os
import csv
from scripts.db_utils import add_data_async, async_session, add_data_async_repo_activity

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


async def add_top_100(first_time: bool):
    limit = 100
    gql_format = """query{
        search(query: "%s", type: REPOSITORY, first:%d) {
          pageInfo { endCursor }
                    edges {
                        node {
                            ...on Repository {
                                name
                                owner {
                                    login
                                }
                                stargazerCount
                                watchers {
                                  totalCount
                                }
                                forkCount
                                openIssues: issues(states: OPEN) {
                                    totalCount
                                }
                                primaryLanguage {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'bearer {}'.format(GITHUB_TOKEN),
    }
    gql_stars = gql_format % ("stars:>1000 sort:stars", limit)
    s = requests.session()
    s.keep_alive = False  # don't keep the session
    graphql_api = "https://api.github.com/graphql"
    r = requests.post(url=graphql_api, json={"query": gql_stars}, headers=headers, timeout=30)
    data = r.json()
    list_of_repos = []
    counter_pos = 1
    counter_id = 1
    field_names = [
        "id",
        "name",
        "owner",
        "position_cur",
        "position_prev",
        "stargazerCount",
        "watcherCount",
        "forkCount",
        "openIssuesCount",
        "primaryLanguage"
    ]
    csv_file_path_curr = 'data/top_100_current.csv'
    csv_file_path_prev = 'data/top_100_previous.csv'
    tasks = []
    if first_time:
        for repo in data['data']["search"]['edges']:
            row_dict = {
                "id": counter_pos,
                "name": repo['node']['name'],
                "owner": repo['node']['owner']['login'],
                "position_cur": counter_pos,
                "position_prev": sqlalchemy.sql.null(),
                "stargazerCount": repo['node']['stargazerCount'],
                "watcherCount": repo['node']['watchers']['totalCount'],
                "forkCount": repo['node']['forkCount'],
                "openIssuesCount": repo['node']['openIssues']['totalCount'],
                "primaryLanguage":
                    repo['node']['primaryLanguage']['name'] if
                    repo['node']['primaryLanguage'] is not None else sqlalchemy.sql.null()
            }
            list_of_repos.append(row_dict)
            counter_pos += 1
            task = asyncio.create_task(
                add_data_async(row_dict))
            tasks.append(task)

        with open(csv_file_path_curr, "w", newline="", encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter="[")
            for repo in list_of_repos:
                writer.writerow(repo)
        with open(csv_file_path_prev, "w", newline="", encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter="[")
            for repo in list_of_repos:
                writer.writerow(repo)
    else:
        prev_pos_dict = {}
        with open(csv_file_path_curr, "r") as csv_file:
            reader = csv.reader(csv_file, delimiter="[")
            with open(csv_file_path_prev, "w", newline="", encoding='utf-8') as csv_file_prev:
                for row in reader:
                    if counter_id == 1:
                        counter_id += int(row[0]) + 99
                    writer = csv.writer(csv_file_prev, delimiter="[")
                    writer.writerow(row)
                    prev_pos_dict[str(row[1]) + str(row[2])] = int(row[3])
        for repo in data['data']["search"]['edges']:
            name = str(repo['node']['name'])
            owner = str(repo['node']['owner']['login'])
            row_dict = {
                "id": counter_id,
                "name": repo['node']['name'],
                "owner": repo['node']['owner']['login'],
                "position_cur": counter_pos,
                "position_prev":
                    prev_pos_dict[name + owner]
                    if prev_pos_dict[name + owner]
                       is not None else sqlalchemy.sql.null(),
                "stargazerCount": repo['node']['stargazerCount'],
                "watcherCount": repo['node']['watchers']['totalCount'],
                "forkCount": repo['node']['forkCount'],
                "openIssuesCount": repo['node']['openIssues']['totalCount'],
                "primaryLanguage":
                    repo['node']['primaryLanguage']['name'] if
                    repo['node']['primaryLanguage'] is not None else sqlalchemy.sql.null()
            }
            list_of_repos.append(row_dict)
            task = asyncio.create_task(
                add_data_async(row_dict))
            tasks.append(task)
            counter_pos += 1
            counter_id += 1
        with open(csv_file_path_curr, "w", newline="", encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter="[")
            for repo in list_of_repos:
                writer.writerow(repo)
    responses = await asyncio.gather(*tasks)


async def get_repo_activity_(params):
    repo_activity = """
        {
            repository(owner: "%s", name: "%s") {
              nameWithOwner
              defaultBranchRef {
                name
                target {
                  ... on Commit {
                    history(since: "%s", until: "%s") {
                      totalCount
                        nodes {
                          committedDate
                          author {
                            name
                          }
                      }
                    }
                  }
                }
              }
            }
          }
        """
    repo_activity_true = repo_activity % (params["owner"], params["repo"],
                                          params["since"].strftime(
                                              "%Y-%m-%dT%H:%M:%S"),
                                          params["until"].strftime(
                                              "%Y-%m-%dT%H:%M:%S"))
    json_resp = await get_url(repo_activity_true)
    sub_dict = {}
    for row in json_resp["data"]["repository"]["defaultBranchRef"]["target"]["history"]["nodes"]:
        temp_date = row["committedDate"][0:10]
        if temp_date in sub_dict.keys():
            sub_dict[temp_date]["commits"] += 1
            sub_dict[temp_date]["authors"].append(row["author"]["name"])
        else:
            sub_dict[temp_date] = {"commits": 1, "authors": [row["author"]['name']]}
    tasks=[]
    for key, item in sub_dict.items():
        task = asyncio.create_task(
            add_data_async_repo_activity({"date": datetime.strptime(key, "%Y-%m-%d"), "commits": item['commits'],
                              "authors": list(set(item['authors']))}))
        tasks.append(task)
    return await asyncio.gather(*tasks)


async def get_url(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'bearer {}'.format(GITHUB_TOKEN),
    }
    graphql_api = "https://api.github.com/graphql"
    timeout = aiohttp.ClientTimeout(total=30)
    conn = aiohttp.TCPConnector(limit_per_host=20)
    cookie_jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(trust_env=True, headers=headers, timeout=timeout, connector=conn,
                                     cookie_jar=cookie_jar) as session:
        try:
            async with session.post(graphql_api, json={"query": query}, ssl=False) as response:
                return await response.json()
        except Exception as e:
            print(e)
            raise e
# df= pd.read_csv('test.csv')
# print(df.head())
# if False==True:
#     create_db()
#     loop = asyncio.get_event_loop()
#     res = loop.run_until_complete(make_top_100(True))
# else:
#     loop = asyncio.get_event_loop()
#     res = loop.run_until_complete(make_top_100(False))

# make_top_100(False)
