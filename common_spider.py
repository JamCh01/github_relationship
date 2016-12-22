import requests
from bs4 import BeautifulSoup
import gevent
from gevent import monkey
monkey.patch_all()
res = {}



class github_spider(object):

    def __init__(self):
        self.base_url = 'https://github.com/'

    def __get_page(self, url):
        r = requests.get(url=url)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'html.parser')
        return soup

    def user_info(self, username):
        try:
            node = self.__get_page(url='%s%s' % (self.base_url, username))
            email = node.find('li', {'aria-label': 'Email'}).text.strip()
        except Exception as e:
            email = ''
        return {'username': username, 'email': email}


    def __relationship(self, username, action, page):
        tmp = []
        try:
            # 遍历用户列表
            node = self.__get_page(
                url='%s%s/?page=%s&tab=%s' %
                (self.base_url, username, page, action))
            all_user_node = node.find(
                'div', {'class': 'js-repo-filter position-relative'})
            users_node = all_user_node.find_all(
                'div', {
                    'class': 'd-table col-12 width-full py-4 border-bottom border-gray-light'})
            if users_node == []:
                return tmp
            for i in users_node:
                user = i.find('span', {'class': 'link-gray pl-1'}).text
                tmp.append(user)
        except Exception as e:
            pass
        return tmp

    def user_relationship(self, username, action):
        result = []
        page = 1
        while True:
            tmp = self.__relationship(username=username,action=action,page=page)
            if len(tmp) == 0:
                break
            else:
                result += tmp
            page += 1
        return result


new = github_spider()



def info(username):
    res['user_info'] = new.user_info(username=username)

def followers(username):
    res['followers'] = new.user_relationship(username=username, action='followers')

def following(username):
    res['following'] = new.user_relationship(username=username, action='following')


def user_info(username):
    gevent.joinall([
        gevent.spawn(followers, username),
        gevent.spawn(following, username),
    ])
    each = set(res['followers']) & set(res['following'])  # 互相关注为关注者和粉丝的交集
    res['followers'] = list(set(res['followers']) -
                            each)  # 根据关注和粉丝与互相关注的差集去掉重复数据
    res['following'] = list(set(res['following']) - each)
    res['each'] = list(each)
    return res
