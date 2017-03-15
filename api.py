import re
import math
import requests
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup


class github(object):

    def __init__(self, user_name):
        self.user_name = user_name

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
        r = s.get(url=url, timeout=30, headers=headers)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'lxml')
        return soup

    @property
    def count(self):
        # 获得用户的repo，star，followers，following总数
        soup = self.spider(url='https://github.com/{}'.format(self.user_name))
        try:
            repo = soup.find(
                'a', {
                    'href': '/{}?tab=repositories'.format(
                        self.user_name)}).find(
                'span', {
                    'class': 'counter'}).text.strip()
        except Exception as e:
            repo = '0'
        try:
            stars = soup.find('a',
                              {'href': '/{}?tab=stars'.format(self.user_name)}).find('span',
                                                                                     {'class': 'counter'}).text.strip()
        except Exception as e:
            stars = '0'
        try:
            followers = soup.find(
                'a', {
                    'href': '/{}?tab=followers'.format(
                        self.user_name)}).find(
                'span', {
                    'class': 'counter'}).text.strip()
        except Exception as e:
            followers = '0'
        try:
            following = soup.find(
                'a', {
                    'href': '/{}?tab=following'.format(
                        self.user_name)}).find(
                'span', {
                    'class': 'counter'}).text.strip()
        except Exception as e:
            following = '0'

        res = {
            'repositories': repo,
            'stars': stars,
            'followers': followers,
            'following': following
        }
        return res

    def data(self, action):
        total = self.count[action]
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
        if action == 'repo' or action =='stars':
            count_page = math.ceil(total / 30)
        else:
            count_page = math.ceil(total / 50)
        page = 1

        while page <= count_page:
            urls.append(
                'https://github.com/{}?page={}&tab={}'.format(self.user_name, str(page), action))
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
            pass
        return users

    def repo(self, url):
        soup = self.spider(url=url)
        repos = []
        try:
            all_repos_node = soup.find('div', {'id': 'user-repositories-list'})
            repos_node = all_repos_node.find_all(
                'li', {'class': 'col-12 d-block width-full py-4 border-bottom public fork'})

            for i in repos_node:
                repo = i.find('h3').text.strip()
                # url = 'https://github.com/{}'.format(i.find('a')['href'])
                repos.append(repo)
        except Exception as e:
            pass
        finally:
            return repos

    def star(self, url):
        soup = self.spider(url=url)
        stars = []
        try:
            all_repos_node = soup.find(
                'div', {'class': 'js-repo-filter position-relative'})
            repos_node = all_repos_node.find_all(
                'div', {'class': 'd-inline-block mb-1'})


            for i in repos_node:
                star = i.find('h3').text.strip()
                # url = 'https://github.com/{}'.format(i.find('a')['href'])
                stars.append(star)
        except Exception as e:
            print(e)
        finally:
            return stars
