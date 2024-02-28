import json

import requests

limit = 100
gql_format = """query{
    search(query: "%s", type: REPOSITORY, first:%d) {
      pageInfo { endCursor }
                edges {
                    node {
                        ...on Repository {
                            id
                            name
                            url
                            forkCount
                            stargazers {
                                totalCount
                            }
                            owner {
                                login
                            }
                            description
                            pushedAt
                            primaryLanguage {
                                name
                            }
                            openIssues: issues(states: OPEN) {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
        """



def get_access_token():
    return "asdasdasdasdasd"


access_token = get_access_token()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': 'bearer {}'.format(access_token),
}
gql_stars = gql_format % ("stars:>1000 sort:stars", limit)
s = requests.session()
s.keep_alive = False  # don't keep the session
graphql_api = "https://api.github.com/graphql"
r = requests.post(url=graphql_api, json={"query": gql_stars}, headers=headers, timeout=30)
print(r.json())
data = r.json()

# Specify the file path where you want to save the JSON file
file_path = "data.json"

# Open the file in write mode and save the data as JSON
with open(file_path, "w") as json_file:
    json.dump(data, json_file)
