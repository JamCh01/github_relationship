import re
import orm
import math
import queue
import requests
import threading
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

followers_page = queue.Queue()
following_page = queue.Queue()

followers = queue.Queue()
following = queue.Queue()



followers_lock = threading.Lock()
following_lock = threading.Lock()


class github(object):

    def __init__(self):
        pass

    def spider(self, url):
        s = requests.Session()
        https_retries = Retry(100)
        https = requests.adapters.HTTPAdapter(max_retries=https_retries)
        s.mount('https://', https)
        r = s.get(url=url, timeout=30)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'html.parser')
        return soup

    def total(self, user_name):
        soup = self.spider(url='https://github.com/{}'.format(user_name))
        nums = soup.find_all('span', {'class': 'counter'})
        res = {
            'Repositories': '',
            'Stars': '',
            'Followers': '',
            'Following': ''
        }
        i = 0
        for v in res.keys():
            res[v] = [i.text for i in nums][i]
            i += 1
        return res

    def follow(self, user_name, action):

        if action == 'followers':
            total = self.total(user_name=user_name)['Followers']
        else:
            total = self.total(user_name=user_name)['Following']

        if total == '0':
            return
        elif 'k' in total:
            total = (
                float(
                    re.findall(
                        pattern=r'^[1-9]*[.]?[1-9]*',
                        string=total)[0]) + 0.1) * 1000 - 1
        else:
            total = float(total)

        return math.ceil(total / 50)

    def relationship(self, user_name, action, page):
        page = str(int(page + 1))
        soup = self.spider(
            url='https://github.com/{}?page={}&tab={}'.format(user_name, page, action))
        users = []
        try:
            all_user_node = soup.find(
                'div', {'class':
                            'js-repo-filter position-relative'})
            users_node = all_user_node.find_all(
                'div', {'class':
                            'd-table col-12 width-full py-4 border-bottom border-gray-light'})
            if users_node == []:
                return users
            for i in users_node:
                user = i.find('span', {'class':
                                           'link-gray pl-1'}).text
                users.append(user)
        except NameError:
            pass
        finally:
            return users

class followers_producer(threading.Thread, github):

    def __init__(self, user_name, max_page):
        threading.Thread.__init__(self)
        for i in range(max_page):
            followers_page.put(i)
        self.user_name = user_name
        self.action = 'followers'

    def run(self):
        while True:
            if followers_page.empty():
                break
            users = github().relationship(
                user_name=self.user_name,
                action=self.action,
                page=followers_page.get())
            for i in users:
                followers.put(i)


class followers_consumer(threading.Thread, github):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if followers.empty():
                break
            followers_lock.acquire()
            user_name = followers.get()
            print(user_name)
            followers_lock.release()


class following_producer(threading.Thread, github):

    def __init__(self, user_name, max_page):
        threading.Thread.__init__(self)
        for i in range(max_page):
            following_page.put(i)
        self.user_name = user_name
        self.action = 'following'

    def run(self):
        while True:
            if following_page.empty():
                break
            users = github().relationship(
                user_name=self.user_name,
                action=self.action,
                page=following_page.get())
            for i in users:
                following.put(i)


class following_consumer(threading.Thread, github):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if following.empty():
                break
            following_lock.acquire()
            user_name = following.get()
            print(user_name)
            following_lock.release()
            pass
        
def find_all_level(level):
    find_session = orm.DBSession()
    users = []
    res = find_session.query(orm.relationship).filter_by(
        level = level).all()
    for i in res:
        users.append(i.user_name)
    find_session.close()
    return users


def check_relationship(username, referer):
    # 校验是否存在本关系
    # 不存在时候插入
    check_session = orm.DBSession()
    try:
        check_session.query(orm.relationship).filter_by(
            user_name = username,
            referer = referer).one()
        return False
    except Exception as e:
        return True
    finally:
        check_session.close()


def main(user_name):
    _followers_producer = followers_producer(user_name=user_name,
                                             max_page=github().follow(user_name=user_name, action=followers))
    _following_producer = following_producer(user_name=user_name,
                                             max_page=github().follow(user_name=user_name, action=following))

    _followers_producer.run()
    _following_producer.run()

    _followers_consumer = followers_consumer()
    _following_consumer = following_consumer()

    _followers_consumer.run()
    _following_consumer.run()

if __name__ == '__main__':
    main(user_name = 'jamcplusplus')