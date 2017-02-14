from gevent import monkey
monkey.patch_all()
import re
import orm
import math
import queue
import gevent
import logging
import requests
import datetime
import threading
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

followers_page = queue.Queue()
following_page = queue.Queue()
data_queue = queue.Queue()

class github(object):
    res = {}

    def __init__(self):
        pass


    def spider(self, url):
        with requests.Session() as s:
            https_retries = Retry(100)
            https = requests.adapters.HTTPAdapter(max_retries=https_retries)
            s.mount('https://', https)
            r = s.get(url=url, timeout=30,headers={'Connection':'close'})
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

        for k,v in zip(res.keys(),nums):
            res[k] = v.text.strip()

        return res

    def follow(self, user_name, action):

        if action == 'followers':
            total = self.total(user_name=user_name)['Followers']
        else:
            total = self.total(user_name=user_name)['Following']

        if total == '0':
            return 0
        elif 'k' in total:
            total = (float(re.findall(pattern=r'^[1-9]*[.]?[1-9]*',string=total.strip())[0]) + 0.1) * 1000 - 1
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



# 根据页面总数，开启相应数目的followers，following进程

class relation(threading.Thread,github):
    def __init__(self,user_name,action,page):
        threading.Thread.__init__(self)
        self.user_name = user_name
        self.action = action
        self.page = page

    def run(self):
        users = github().relationship(user_name=self.user_name,action=self.action,page=self.page)
        if users == []:
            return
        for user in users:
            data = {
                'user_name': user,
                'level': level + 1,
                'action': self.action,
                'referer': self.user_name
            }
            data_queue.put(data)

class followers_producer(threading.Thread, github):

    def __init__(self, user_name, max_page):
        threading.Thread.__init__(self)
        self.max_page = max_page
        self.user_name = user_name
        self.action = 'followers'

    def run(self):
        tasks = []
        # todo 更改开启线程数
        if self.max_page <= 300:
            for i in range(self.max_page):
                task = relation(user_name=self.user_name, action=self.action, page=i)
                tasks.append(task)
            for _task in tasks:
                _task.start()
            for _task in tasks:
                _task.join()
        else:
            tmp = list(range(self.max_page))
            while  tmp != []:
                for i in tmp[::300]:
                    task = relation(user_name=self.user_name, action=self.action, page=i)
                    tasks.append(task)
                    tmp.remove(i)
                for _task in tasks:
                    _task.start()
                for _task in tasks:
                    _task.join()
                tasks = []

class following_producer(threading.Thread, github):
    def __init__(self, user_name, max_page):
        threading.Thread.__init__(self)
        self.max_page = max_page
        self.user_name = user_name
        self.action = 'following'

    def run(self):
        tasks = []
        if self.max_page <= 300:
            for i in range(self.max_page):
                task = relation(user_name=self.user_name, action=self.action, page=i)
                tasks.append(task)
            for _task in tasks:
                _task.start()
            for _task in tasks:
                _task.join()

        else:
            tmp = list(range(self.max_page))
            while  tmp != []:
                for i in tmp[::300]:
                    task = relation(user_name=self.user_name, action=self.action, page=i)
                    tasks.append(task)
                    tmp.remove(i)
                for _task in tasks:
                    _task.start()
                for _task in tasks:
                    _task.join()
                tasks = []

class consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        consumer_session = orm.DBSession()
        while True:
            if data_queue.empty():
                consumer_session.close()
                break
            data = data_queue.get()
            user_name = data['user_name']
            referer = data['referer']
            action = data['action']
            level = data['level']

            if check_relationship(
                    username=user_name,
                    referer=referer):
                pass
            else:
                new_user = orm.relationship(
                    user_name=user_name,
                    level=level,
                    type=action,
                    referer=referer)
                consumer_session.add(new_user)
                consumer_session.commit()

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
            user_name = username,referer = referer).one()
        return True
    except Exception as e:
        return False
    finally:
        check_session.close()

def followers(user_name):
    _followers_producer = followers_producer(user_name=user_name,
                                             max_page=github().follow(user_name=user_name, action='followers'))
    _followers_producer.run()

def following(user_name):
    _following_producer = following_producer(user_name=user_name,
                                             max_page=github().follow(user_name=user_name, action='following'))
    _following_producer.run()


def main(user_name):
    gevent.joinall([
        gevent.spawn(followers, user_name),
        gevent.spawn(following, user_name),
    ])
    gevent.get_hub().join()
    tasks = []
    for i in range(10):
        _consumer = consumer()
        tasks.append(_consumer)
    for _task in tasks:
        _task.start()
    for _task in tasks:
        _task.join()






if __name__ == '__main__':
    log_file = "./basic_logger.log"
    logging.basicConfig(filename=log_file, level=logging.INFO)

    session = orm.DBSession()
    username = 'jamcplusplus'
    level = 0
    referer = username
    type = 'self'

    init_user = orm.relationship(
        user_name=username,
        level=level,
        type=type,
        referer=referer)
    session.add(init_user)
    session.commit()
    session.close()
    while level != 6:
        start_time = datetime.datetime.now()
        for i in find_all_level(level=level):
            main(user_name=i)
        level += 1
        end_time = datetime.datetime.now()
        print('level %s cost %s' % (level, end_time - start_time))
