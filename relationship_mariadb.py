from gevent import monkey
monkey.patch_all()
import gc
import queue
import datetime
import gevent
import requests
import threading
# import pymysql as mariadb
# Threads may share the module, but not connections.
# 线程可以共享模块，但不能共享连接。
# https://www.python.org/dev/peps/pep-0249/#threadsafety
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

server_chan_url = 'http://sc.ftqq.com/SCU4819T4a9424bcfd09b1c39cee36cae6309d9758648caace3a6.send'

def dimension(level):
    data = {
        'text': '用户纬度%s已经抓取完成(。・`ω´・)' % level,
        'desp': '''本次抓取共耗时：%s (￣_,￣ )''' % (end_time - start_time)
    }
    r = requests.post(url=server_chan_url, data=data)

# def total():
#     tmp_session = DBSession()
#     res = tmp_session.query(relationship).count()
#     data = {
#         'text':'%s 总计' % datetime.datetime.now(),
#         'desp':res
#     }
#     r = requests.post(url=server_chan_url, data=data)
#     return None


def find_all_level(level):
    tmp_session = DBSession()
    users = []
    res = tmp_session.query(relationship).filter(
        relationship.level == level).all()
    for i in res:
        users.append(i.user_name)
    tmp_session.close()
    return users


def check_relationship(username, referer):
    # 校验是否存在本关系
    # 不存在时候插入
    try:
        session.query(relationship).filter(
            relationship.user_name == username,
            relationship.referer == referer).one()
        return False
    except Exception as e:
        return True


# followers生产者<->followers消费者
# following生产者<->following消费者
class github_spider(object):
    '''
    爬虫类
    '''

    def __init__(self):
        self.base_url = 'https://github.com/'

    def __get_page(self, url):
        '''
        获得页面html
        :param url:用户对应页面
        :return: 页面soup对象
        '''
        s = requests.Session()
        https_retries = Retry(60)
        https = requests.adapters.HTTPAdapter(max_retries=https_retries)
        s.mount('https://', https)
        r = s.get(url=url, timeout=60)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'html.parser')
        return soup

    def user_info(self, username):
        '''
        用户信息页
        :param username:用户名
        :return: dict[username],dict[email]
        '''
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
        page = 1
        while True:
            tmp = self.__relationship(
                username=username, action=action, page=page)
            if tmp == []:
                with open('log.txt', 'a') as f:
                    f.write('%s %s %s %s page break\n' %
                            (str(datetime.datetime.now()), username, action, page))
                f.close()
                break
            with open('log.txt', 'a') as f:
                f.write('%s %s %s %s page running\n' %
                        (str(datetime.datetime.now()), username, action, page))
            f.close()
            if action == 'followers':
                _followers_producer = followers_producer(tmp=tmp)
                _followers_consumer = followers_consumer()
                _followers_producer.start()
                _followers_producer.join()
                _followers_consumer.start()
            elif action == 'following':
                _following_producer = following_producer(tmp=tmp)
                _following_consumer = following_consumer()
                _following_producer.start()
                _following_producer.join()
                _following_consumer.start()
            page += 1


class followers_producer(threading.Thread):
    '''
    followers生产者
    '''

    def __init__(self, tmp):
        threading.Thread.__init__(self)
        threading.Thread.name = 'followers_producer'
        self.tmp = tmp
        self.data = followers_queue

    def run(self):
        followers_lock.acquire()
        for i in self.tmp:
            # print(i)
            self.data.put(i)


class following_producer(threading.Thread):
    '''
    following生产者
    '''

    def __init__(self, tmp):
        threading.Thread.__init__(self)
        threading.Thread.name = 'following_producer'
        self.tmp = tmp
        self.data = following_queue

    def run(self):
        following_lock.acquire()
        for i in self.tmp:
            # print(i)

            self.data.put(i)


class followers_consumer(threading.Thread):
    '''
    followers的消费者
    '''

    def __init__(self):
        threading.Thread.__init__(self)
        threading.Thread.name = 'followers_consumer'
        self.referer = referer

    def run(self):
        followers_lock.release()
        while True:
            follower_session = DBSession()
            try:
                user_name = followers_queue.get()
                if check_relationship(
                        username=user_name,
                        referer=referer):
                    new_follower = relationship(
                        user_name=user_name,
                        level=level + 1,
                        type='follower',
                        referer=referer)
                    follower_session.add(new_follower)
                    follower_session.commit()
                    follower_session.close()
            except Exception as e:
                follower_session.close()
                break


class following_consumer(threading.Thread):
    '''
    following的消费者
    '''

    def __init__(self):
        threading.Thread.__init__(self)
        threading.Thread.name = 'following_consumer'
        self.referer = referer

    def run(self):
        following_lock.release()
        # following线程连接
        while True:
            following_session = DBSession()
            try:
                user_name = following_queue.get()

                if check_relationship(
                        username=user_name,
                        referer=referer):
                    new_following = relationship(
                        user_name=user_name,
                        level=level + 1,
                        type='following',
                        referer=referer)
                    following_session.add(new_following)
                    following_session.commit()
                    following_session.close()
            except Exception as e:
                following_session.close()
                break


def followers(username):
    new.user_relationship(username=username, action='followers')


def following(username):
    new.user_relationship(username=username, action='following')


def user_info(username):
    gevent.joinall([
        gevent.spawn(followers, username),
        gevent.spawn(following, username),
    ])
    gevent.get_hub().join()

if __name__ == '__main__':
    new = github_spider()
    # 创建连接
    # '数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名'
    engine = create_engine('mysql+pymysql://github:test@localhost/github')
    # 创建表
    metadata = MetaData(engine)
    user = Table('relationship', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('user_name', String(256)),
                 Column('referer', String(256)),
                 Column('level', Integer),
                 Column('type', String(256))
                 )
    metadata.create_all()
    # 创建对象的基类
    Base = declarative_base()
    # 定义User对象:

    class relationship(Base):
        # 表名:
        __tablename__ = 'relationship'
        # 表结构:
        id = Column(Integer, primary_key=True)
        user_name = Column(String(256))
        level = Column(Integer)
        referer = Column(String(256))
        type = Column(String(256))

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    # 目标用户
    username = 'HolaJam'
    # 初始等级
    level = 0
    # 初始referer
    referer = username
    # 初始关系类型
    type = 'self'
    # 加入初始用户
    # 创建新User对象:
    new_user = relationship(
        user_name=username,
        level=level,
        type=type,
        referer=referer)
    # 添加到session:
    session.add(new_user)
    # 提交即保存到数据库:
    session.commit()
    # followers生产者队列
    followers_queue = queue.Queue()
    # following生产者队列
    following_queue = queue.Queue()
    # 对线程上锁
    # followers锁
    followers_lock = threading.Lock()
    # following锁
    following_lock = threading.Lock()
    session.close()
    while level != 6:
        start_time = datetime.datetime.now()
        for i in find_all_level(level=level):
            referer = i
            user_info(username=i)
            gc.collect()
        level += 1
        end_time = datetime.datetime.now()
        print('level %s cost %s' % (level, end_time - start_time))
        dimension(level=level)



# 消费者 - 生产者 模型基本完成，在INSERT时候不会消耗太多时间
# todo 完善其他功能
# todo 增加抓取的多线程
