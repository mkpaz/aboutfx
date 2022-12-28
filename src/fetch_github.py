import json
import math
from time import sleep
from urllib.request import Request, urlopen

GITHUB_API = 'https://api.github.com'
DATASET_DIR = './dataset/github/uncompressed'

def start():
    fetchStars()
    fetchPullRequests()
    fetchRecentlyUpdatedRepos()
    fetchRepoGrowth()

def fetchRepoGrowth():
    base = GITHUB_API + '/search/repositories?q=topic:javafx%20'

    stats = []
    for year in range(2012, 2023):
        for month in range(1, 13):
            yearMonth = '{}-{:02d}'.format(year, month)
            url = base + 'created:{}&per_page=1'.format(yearMonth)
            req = Request(url)
            req.add_header('Accept', 'application/vnd.github+json')
            #req.add_header('Authorization', 'token %s' % TOKEN)

            data = json.loads(urlopen(req).read())
            stats.append({'date': yearMonth, 'count': data['total_count']})
            print(url, {'date': yearMonth, 'count': data['total_count']})
            sleep(5)  # timeout to avoid rate limit

    with open(DATASET_DIR + '/repo-stats.json', 'w') as file:
        json.dump(stats, file, indent=2)

def fetchRecentlyUpdatedRepos():
    # GitHub search is limited to 1000 result (paginated or not),
    # there will be 422 after that. So, we have to narrow the search query,
    # but the fetched result will contain duplicates we have to remove later.
    base = GITHUB_API + '/search/repositories?q=topic:javafx%20pushed:%3E2020-01-01%20'
    for year in range(2012, 2023):
        fetchRepoQuery(base + 'created:{}-01-01..{}-06-30'.format(year, year), str(year) + '_0')
        fetchRepoQuery(base + 'created:{}-07-01..{}-12-31'.format(year, year), str(year) + '_1')


def fetchRepoQuery(baseUrl, id):
    response = urlopen(baseUrl + '&per_page=1')
    stats = json.loads(response.read())
    pageCount = math.ceil(stats['total_count'] / 100)

    repos = []
    for n in range(1, pageCount + 1):
        req = Request(baseUrl + '&page={}&per_page=100&sort=stars'.format(n))
        req.add_header('Accept', 'application/vnd.github+json')
        #req.add_header('Authorization', 'token %s' % TOKEN)

        page = urlopen(req)
        pageData = json.loads(page.read())
        repos.append(pageData)

        sleep(5) # timeout to avoid rate limit

    with open(DATASET_DIR + '/repos_{}.json'.format(id), 'w') as file:
        json.dump(repos, file, indent = 2)


def fetchPullRequests():
    response = urlopen(GITHUB_API + '/search/issues?q=repo:openjdk/jfx%20is:pr&per_page=1')
    data = json.loads(response.read())
    prCount = data['total_count']

    pulls = []
    pageCount = math.ceil(prCount / 100)

    for n in range(1, pageCount + 1):
        url = GITHUB_API + '/repos/openjdk/jfx/pulls?state=all&page={}&per_page=100'.format(n)
        req = Request(url)
        req.add_header('Accept', 'application/vnd.github+json')
        #req.add_header('Authorization', 'token %s' % TOKEN)

        page = urlopen(req)
        pageData = json.loads(page.read())
        pulls.append(pageData)

    with open(DATASET_DIR + 'pull-requests.json', 'w') as file:
        json.dump(pulls, file, indent = 2)


def fetchStars():
    response = urlopen(GITHUB_API + '/repos/openjdk/jfx')
    data = json.loads(response.read())
    starCount = data['stargazers_count']

    stars = []
    pageCount = math.ceil(starCount / 100)
    for n in range(1, pageCount + 1):
        url = GITHUB_API + '/repos/openjdk/jfx/stargazers?page={}&per_page=100'.format(n)
        req = Request(url)
        req.add_header('Accept', 'application/vnd.github.v3.star+json') # magic value to get starred_at
        #req.add_header('Authorization', 'token %s' % TOKEN)

        page = urlopen(req)
        pageData = json.loads(page.read())
        stars.append(pageData)

    with open(DATASET_DIR + 'stars.json', 'w') as file:
        json.dump(stars, file, indent = 2)
