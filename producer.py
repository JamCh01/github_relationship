from gevent import monkey
monkey.patch_all()
import gevent
import queue
import threading
from api import github
from config import database
data_queue = queue.Queue()
user_queue = queue.Queue()
star_queue = queue.Queue()
repo_queue = queue.Queue()
following_queue = queue.Queue()
followers_queue = queue.Queue()


class producer(threading.Thread):
    """生产者"""

    def __init__(self):
        threading.Thread.__init__(self)

    def get_data(self, user_name):
        tmp = github(user_name=user_name)
        data = {
            'user': user_name,
            'following':'',
            'followers':'',
            'repo':'',
            'star':''
        }

        def following():
            data['following'] = tmp.data(action='following')

        def followers():
            data['followers'] = tmp.data(action='followers')

        def repo():
            data['repo'] = tmp.data(action='repositories')

        def star():
            data['star'] = tmp.data(action='stars')

        gevent.joinall([
            gevent.spawn(followers),
            gevent.spawn(following),
            gevent.spawn(repo),
            gevent.spawn(star),
        ])
        data_queue.put(data)

    def run(self):
        while not user_queue.empty():
            self.get_data(user_name=user_queue.get())


class scheduler(threading.Thread):
    """调度器，将data_queue中数据细化至其他queue"""

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not data_queue.empty():
            info = data_queue.get()
            print(info)

            def star():
                star_queue.put({'user': info['user'], 'star': info['star']})

            def repo():
                repo_queue.put({'user': info['user'], 'repo': info['repo']})

            def following():
                following_queue.put(
                    {'user': info['user'], 'following': info['following']})

            def followers():
                followers_queue.put(
                    {'user': info['user'], 'followers': info['followers']})

            gevent.joinall([
                gevent.spawn(followers),
                gevent.spawn(following),
                gevent.spawn(repo),
                gevent.spawn(star),
            ])


class consumer(threading.Thread):

    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        def star():
            while not star_queue.empty():
                info = star_queue.get()
                user = info['user']
                tmp = github(user_name=user)
                for url in info['star']:
                    repos = tmp.star(url=url)
                    for repo_name in repos:
                        project_owner = repo_name.split('/')[0]
                        project_name = repo_name.split('/')[1]
                        database().star(
                            referer_user=user,
                            project_name=project_name,
                            project_url=' ',
                            project_owner=project_owner)

        def repo():
            while not repo_queue.empty():
                info = repo_queue.get()
                user = info['user']
                tmp = github(user_name=user)
                for url in info['repo']:
                    repos = tmp.repo(url=url)
                    for repo_name in repos:
                        database().repo(
                            project_user=user,
                            project_name=repo_name,
                            project_url=' ')

        def following():
            while not following_queue.empty():
                info = following_queue.get()
                user = info['user']
                tmp = github(user_name=user)
                for url in info['following']:
                    followings = tmp.user(url=url)
                    for following in followings:
                        database().relationship(
                            user_name=following,
                            referer=user,
                            level=level,
                            action='following'
                        )

        def followers():
            while not followers_queue.empty():
                info = followers_queue.get()
                user = info['user']
                tmp = github(user_name=user)
                for url in info['followers']:
                    followers = tmp.user(url=url)
                    for follower in followers:
                        database().relationship(
                            user_name=follower,
                            referer=user,
                            level=level,
                            action='following'
                        )

        gevent.joinall([
            gevent.spawn(eval(self.action))
        ])


def main(level):



    for user in database().find_level(level=level-1):
        user_queue.put(user)

    # 生产者线程
    producer_tasks = []
    for i in range(300):
        run_producer = producer()
        producer_tasks.append(run_producer)
    for task in producer_tasks:
        task.start()
    for task in producer_tasks:
        task.join()

    # 调度线程
    run_scheduler = scheduler()
    run_scheduler.start()
    run_scheduler.join()

    # 消费者线程
    consumer_tasks = []
    for i in range(100):
        run_consumer_star = consumer(action='star')
        run_consumer_repo = consumer(action='repo')
        run_consumer_following = consumer(action='following')
        run_consumer_followers = consumer(action='followers')
        consumer_tasks.append(run_consumer_star)
        consumer_tasks.append(run_consumer_repo)
        consumer_tasks.append(run_consumer_following)
        consumer_tasks.append(run_consumer_followers)

    for task in consumer_tasks:
        task.start()

    for task in consumer_tasks:
        task.join()


if __name__ == '__main__':
    level = 0
    # 初始化用户
    database().init_user()
    while level != 7:
        level += 1
        print(level)
        main(level=level)


