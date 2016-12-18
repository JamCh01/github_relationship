import api
import gevent
from gevent import monkey

res = {}
new = api.github_spider()
def info(username):
    res['user_info'] = new.user_info(username=username)


def followers(username):
    res['followers'] = new.user_followers(username=username)


def following(username):
    res['following'] = new.user_following(username=username)


def starred(username):
    res['starred'] = new.user_starred(username=username)


def repos(username):
    res['repos'] = new.user_repos(username=username)


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
