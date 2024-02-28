import json
from datetime import datetime
import requests
import pandas as pd
import sqlalchemy as sqlalchemy

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


def get_access_token():
    return "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"


access_token = get_access_token()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': 'bearer {}'.format(access_token),
}
gql_stars = gql_format % ("stars:>1000 sort:stars", limit)

repo_activity_true = repo_activity % ("EbookFoundation", "free-programming-books",
                                      datetime.strptime("2024-02-10", "%Y-%m-%d").strftime(
                                          "%Y-%m-%dT%H:%M:%S"),
                                      datetime.strptime("2024-02-28", "%Y-%m-%d").strftime(
                                          "%Y-%m-%dT%H:%M:%S"))
s = requests.session()
s.keep_alive = False  # don't keep the session
graphql_api = "https://api.github.com/graphql"
r = requests.post(url=graphql_api, json={"query": gql_stars}, headers=headers, timeout=30)
print(r.json())
data = r.json()
list_of_repos = []
# print(r.json())
counter = 1
for repo in data['data']["search"]['edges']:
    list_of_repos.append({
        "name": repo['node']['name'],
        "owner": repo['node']['owner']['login'],
        "position_cur": counter,
        "position_prev": sqlalchemy.sql.null(),
        "stargazerCount": repo['node']['stargazerCount'],
        "watcherCount": repo['node']['watchers']['totalCount'],
        "forkCount": repo['node']['forkCount'],
        "openIssuesCount": repo['node']['openIssues']['totalCount'],
        "primaryLanguage":
            repo['node']['primaryLanguage']['name'] if
            repo['node']['primaryLanguage'] is not None else sqlalchemy.sql.null()
    })
    counter += 1

df = pd.DataFrame(list_of_repos)
print(df.head())

df.to_csv('test.csv', index=False, header=False, sep="_")

# df= pd.read_csv('test.csv')
# print(df.head())
