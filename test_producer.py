import re
import math
import queue
import requests
import threading
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from test_config import database

page_queue = queue.Queue()


class github(object):

    def __init__(self):
        pass
    def spider(self, url):
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Host': 'github.com',
        }

        s = requests.Session()
        https_retries = Retry(100)
        https = requests.adapters.HTTPAdapter(max_retries=https_retries)
        s.mount('https://', https)
        r = s.get(url=url, timeout=10, headers=headers)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'html.parser')
        return soup

    def count(self, user_name):
        # 获得用户的repo，star，followers，following总数
        print(user_name)
        soup = self.spider(url='https://github.com/{}'.format(user_name))
        try:
            repo = soup.find('a',
                             {'href': '/{}?tab=repositories'.format(user_name)}).find('span',
                                                                                      {'class': 'counter'}).text.strip()
        except ValueError:
            repo = 0
        try:
            stars = soup.find('a',
                              {'href': '/{}?tab=stars'.format(user_name)}).find('span',
                                                                                {'class': 'counter'}).text.strip()
        except ValueError:
            stars = 0
        try:
            followers = soup.find('a',
                                  {'href': '/{}?tab=followers'.format(user_name)}).find('span',
                                                                                        {'class': 'counter'}).text.strip()
        except ValueError:
            followers = 0
        try:
            following = soup.find('a',
                                  {'href': '/{}?tab=following'.format(user_name)}).find('span',
                                                                                        {'class': 'counter'}).text.strip()
        except ValueError:
            following = 0

        res = {
            'repo': repo,
            'stars': stars,
            'followers': followers,
            'following': following
        }
        return res

    def follow(self, user_name, action):
        total = self.count(user_name=user_name)[action]
        urls = []
        if total == '0':
            return urls
        elif 'k' in total:
            total = (
                float(
                    re.findall(
                        pattern=r'^[1-9]*[.]?[1-9]*',
                        string=total.strip())[0]) + 0.1) * 1000 - 1
        else:
            total = float(total)

        count_page = math.ceil(total / 50)
        page = 1

        while page <= count_page:
            urls.append(
                'https://github.com/{}?page={}&tab={}'.format(user_name, str(page), action))
            page += 1
        return urls

    def user(self, url):
        soup = self.spider(url=url)
        users = []
        try:
            all_user_node = soup.find(
                'div', {'class':
                            'js-repo-filter position-relative'})
            users_node = all_user_node.find_all(
                'div', {
                    'class': 'd-table col-12 width-full py-4 border-bottom border-gray-light'})
            if users_node == []:
                return users
            for i in users_node:
                user = i.find('span', {'class':
                                           'link-gray pl-1'}).text
                users.append(user)
        except Exception as e:
            print(e)
            pass
        return users

class relationship(threading.Thread, github):

    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        while True:
            if page_queue.empty():
                break
            info = page_queue.get()
            print(info)
            for url in info['{}'.format(self.action)]:
                tmp = self.user(url=url)
                for user in tmp:
                    database().insert(user_name=user, referer=info['user'], action=self.action, level=level)



user_name = ['jamcplusplus']
referer = 'self'
level = 0


def producer(level):
    print('running level {}'.format(level))
    users = database().find_level(level=level)
    print(users)
    for user in users:
        data = {}
        data['user'] = user
        data['following'] = github().follow(user_name=user, action='following')
        data['followers'] = github().follow(user_name=user, action='followers')
        data['referer'] = referer
        page_queue.put(data)

database().init_user()

while level<=6:
    producer(level)
    level += 1
    tasks = []
    for i in range(50):
        following = relationship(action='following')
        followers = relationship(action='followers')
        tasks.append(following)
        tasks.append(followers)
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()
    print('level {} finished'.format({level}))

