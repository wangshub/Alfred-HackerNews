# encoding: utf-8

import sys
from functools import reduce
from workflow import Workflow, ICON_WEB, web
from multiprocessing.dummy import Pool as ThreadPool


def get_top_news():
    base_url = 'https://api.hnpwa.com/v0/{name}/{page}.json'
    max_pages = 15
    name = 'news'
    result = []
    for page in range(1, max_pages):
        url = base_url.format(name=name, page=page)
        req = web.get(url)
        req.raise_for_status()

        if len(req.json()) == 0:
            break
        result = result + req.json()
    return result


def req_hn_api(url):
    req = web.get(url)
    req.raise_for_status()
    req_json = req.json()
    return req_json


def multi_get_top_news():
    base_url = 'https://api.hnpwa.com/v0/{name}/{page}.json'
    max_pages = 15
    name = 'news'
    urls = [base_url.format(name=name, page=i) for i in range(1, max_pages)]
    pool = ThreadPool(max_pages)
    results = pool.map(req_hn_api, urls)
    pool.close()
    pool.join()
    return results


def main(wf):
    posts = wf.cached_data('posts', multi_get_top_news, max_age=60*30)
    posts = reduce(lambda x, y: x + y, posts)
    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for post in posts:
        subtitle = "points: {points} | user: {user} | {time_ago} | comments:{comments_count} | {url}".format(
            points=post['points'],
            user=post['user'],
            time_ago=post['time_ago'],
            comments_count=post['comments_count'],
            url=post['url']
        )
        wf.add_item(title=post['title'],
                    subtitle=subtitle,
                    arg=post['url'],
                    valid=True,
                    icon='./icon.png')

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))