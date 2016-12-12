import api
from py2neo import Graph, Node, Relationship
import gevent
from gevent import monkey
monkey.patch_socket()
new = api.github_spider()

graph = Graph(password='test')
graph.delete_all()
username = 'HolaJam'
level = 0
main_node = Node('user', name=username, level=level, referer='')
graph.create(main_node)

res = {}
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
    each = set(res['followers']) & set(res['following']) # 互相关注为关注者和粉丝的交集
    res['followers'] = list(set(res['followers']) - each) # 根据关注和粉丝与互相关注的差集去掉重复数据
    res['following'] = list(set(res['following']) - each )
    res['each'] = list(each)
    return res

def find_node(level):
    # 获得同等级所有用户节点，遍历之
    user_list = graph.find(label='user', property_key='level', property_value=level)
    return user_list

def draw(res, referer, level):
    # 在neo4j中绘制节点和关系，
    main_node = graph.find_one('user', property_key='name', property_value=referer)
    for key in res.keys():
        for i in res[key]:
            tmp = graph.find_one('user', property_key='name', property_value=i)
            if tmp is None:
                tmp = Node('user', name=i, referer=referer, level=level)
            rel = Relationship(main_node, key, tmp)
            graph.create(rel)
            # todo 已有节点的过滤和正确的关系
while level !=5:
    for i in find_node(level=level):
        print(i['name'])
        res = user_info(username=i['name'])
        draw(res = res, referer=i['name'], level=level+1)
    level += 1
